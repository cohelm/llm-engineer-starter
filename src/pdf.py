import mimetypes
import os
from pathlib import Path

import dotenv

from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.cloud.documentai_v1 import Document

# Load Env Files.
# This will return True if your env vars are loaded successfully
dotenv.load_dotenv()


class DocumentAI:
    """Wrapper class around GCP's DocumentAI API."""
    def __init__(self) -> None:

        self.client_options = ClientOptions(  # type: ignore
            api_endpoint=f"{os.getenv('GCP_REGION')}-documentai.googleapis.com",
            credentials_file=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
        )
        self.client = documentai.DocumentProcessorServiceClient(client_options=self.client_options)
        self.processor_name = self.client.processor_path(
            os.getenv("GCP_PROJECT_ID"),
            os.getenv("GCP_REGION"),
            os.getenv("GCP_PROCESSOR_ID")
        )

    def __call__(self, file_path: Path) -> Document:
        """Convert a local PDF into a GCP document. Performs full OCR extraction and layout parsing."""

        # Read the file into memory
        with open(file_path, "rb") as file:
            content = file.read()

        mime_type = mimetypes.guess_type(file_path)[0]
        raw_document = documentai.RawDocument(content=content, mime_type=mime_type)

        # Configure the process request
        request = documentai.ProcessRequest(
            name=self.processor_name,
            raw_document=raw_document
        )

        result = self.client.process_document(request=request)
        document = result.document

        return document


if __name__ == '__main__':

    # Example Usage
    document_ai = DocumentAI()
    document = document_ai(Path("data/sample.pdf"))
