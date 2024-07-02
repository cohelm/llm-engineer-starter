import mimetypes
import logging
import os
import tempfile
from pathlib import Path
from typing import List

import dotenv
from pypdf import PdfReader, PdfWriter

from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.cloud.documentai_v1 import Document

# Load Env Files.
# This will return True if your env vars are loaded successfully
dotenv.load_dotenv()

logger = logging.getLogger(__name__)


class DocumentAI:
    """Wrapper class around GCP's DocumentAI API."""

    def __init__(self) -> None:

        self.client_options = ClientOptions(  # type: ignore
            api_endpoint=f"{os.getenv('GCP_REGION')}-documentai.googleapis.com",    # noqa: E501
            credentials_file=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        )
        self.client = documentai.DocumentProcessorServiceClient(
            client_options=self.client_options
        )
        self.processor_name = self.client.processor_path(
            os.getenv("GCP_PROJECT_ID"),
            os.getenv("GCP_REGION"),
            os.getenv("GCP_PROCESSOR_ID"),
        )

    def process_pdf(self, file_path: Path) -> Document:
        """Convert a local PDF into a GCP document. Performs full OCR
        extraction and layout parsing. The PDF is limited to 15 pages due to
        restrictions of DocumentAI online processing."""

        # Read the file into memory
        with open(file_path, "rb") as file:
            content = file.read()

        mime_type = mimetypes.guess_type(file_path)[0]
        raw_document = documentai.RawDocument(
            content=content, mime_type=mime_type
        )

        # Configure the process request
        request = documentai.ProcessRequest(
            name=self.processor_name, raw_document=raw_document
        )

        result = self.client.process_document(request=request)
        document = result.document

        return document

    def process_long_pdf(self, file_path: Path) -> List[Document]:
        """Process each page of PDF separately to avoid 15 page limit for
        DocumentAI online processing."""

        reader = PdfReader(file_path)
        documents = []

        logger.info(f"Processing pdf with {len(reader.pages)} pages")

        for i, page in enumerate(reader.pages):

            if i % 10 == 0:
                logger.info(f"Processing page {i + 1} / {len(reader.pages)}")

            writer = PdfWriter()
            writer.add_page(page)

            # Write page pdf file for process_pdf to read
            with tempfile.TemporaryDirectory() as temp:
                file_path = Path(temp) / "page.pdf"

                with open(file_path, "wb") as f:
                    writer.write(f)

                documents.append(self.process_pdf(file_path))

        logger.info("Finished processing pdf")

        return documents

    def __call__(self, file_path: Path) -> str:
        """Process PDF of arbitrary length and return concatenated text."""

        documents = self.process_long_pdf(file_path)
        full_text = ""

        for i, document in enumerate(documents):
            full_text += f"PAGE {i+1}\n"
            full_text += document.text + "\n"

        return full_text


if __name__ == "__main__":

    # Example Usage
    document_ai = DocumentAI()
    document = document_ai(Path("data/sample.pdf"))
