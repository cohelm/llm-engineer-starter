import asyncio
import os
from pathlib import Path
from typing import List
import io

import PyPDF2
import fitz  # PyMuPDF

from google.api_core.client_options import ClientOptions
from google.cloud import documentai
from google.cloud.documentai_v1 import Document

from src.schemas import Block, Page, ParsedDocument


class DocumentParser:
    def __init__(self):
        """
        Initialize the DocumentAI class.

        This class serves as a wrapper around processing PDFs using Google Cloud Platform API.
        It sets up the necessary client options and initializes the DocumentAI client.
        """
        self.client_options = ClientOptions(
            api_endpoint=f"{os.getenv('GCP_REGION')}-documentai.googleapis.com"
        )
        self.client = documentai.DocumentProcessorServiceClient(client_options=self.client_options)
        self.processor_name = self.client.processor_path(
            os.getenv("GCP_PROJECT_ID"),
            os.getenv("GCP_REGION"),
            os.getenv("GCP_PROCESSOR_ID")
        )
        self.MAX_PAGES_PER_REQUEST = 15

    async def process_document(self, file_path: Path) -> ParsedDocument:
        """
        Convert a PDF into a structured OCR representation with blocks.

        Parameters
        ----------
        file_path : Path
            The path to the input PDF file.

        Returns
        -------
        ParsedDocument
            A structured representation of the PDF with pages and blocks of text.
        """
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)

        parsed_pages = []
        for start_page in range(0, total_pages, self.MAX_PAGES_PER_REQUEST):
            end_page = min(start_page + self.MAX_PAGES_PER_REQUEST, total_pages)
            batch_pages = await self.process_batch(file_path, start_page, end_page)
            parsed_pages.extend(batch_pages)

        return ParsedDocument(pages=parsed_pages)

    async def process_batch(self, file_path: Path, start_page: int, end_page: int) -> List[Page]:
        """
        Process a batch of pages from the PDF.

        Parameters
        ----------
        file_path : Path
            The path to the input PDF file.
        start_page : int
            The starting page number of the batch.
        end_page : int
            The ending page number of the batch.

        Returns
        -------
        List[Page]
            A list of processed Page objects for the given batch.
        """
        with open(file_path, "rb") as file:
            pdf_reader = PyPDF2.PdfReader(file)
            pdf_writer = PyPDF2.PdfWriter()
            for i in range(start_page, end_page):
                pdf_writer.add_page(pdf_reader.pages[i])

            batch_pdf = io.BytesIO()
            pdf_writer.write(batch_pdf)
            batch_content = batch_pdf.getvalue()

        raw_document = documentai.RawDocument(content=batch_content, mime_type="application/pdf")
        request = documentai.ProcessRequest(name=self.processor_name, raw_document=raw_document)

        result = await asyncio.to_thread(self.client.process_document, request)
        return self.parse_document(result.document)

    def parse_document(self, document: Document) -> List[Page]:
        """
        Parse the processed document into a list of Page objects.

        Parameters
        ----------
        document : Document
            The processed document from Google Cloud DocumentAI.

        Returns
        -------
        List[Page]
            A list of Page objects containing blocks of text and their positions.
        """
        pages = []
        for page in document.pages:
            blocks = []
            for block in page.blocks:
                vertices = [(v.x, v.y) for v in block.layout.bounding_poly.normalized_vertices]
                text = self.get_text(document, block.layout.text_anchor)
                blocks.append(Block(vertices=vertices, text=text))
            pages.append(Page(blocks=blocks))
        return pages

    @staticmethod
    def get_text(document: Document, text_anchor: Document.TextAnchor) -> str:
        """
        Extract text from the document based on the text anchor.

        Parameters
        ----------
        document : Document
            The processed document from Google Cloud DocumentAI.
        text_anchor : Document.TextAnchor
            The text anchor containing information about text position.

        Returns
        -------
        str
            The extracted text.
        """
        start_index = text_anchor.text_segments[0].start_index
        end_index = text_anchor.text_segments[0].end_index
        return document.text[start_index:end_index]


class PDFAnnotator:
    def __init__(self, input_pdf_path: Path):
        self.pdf_document = fitz.open(input_pdf_path)

    def draw_block(self, page_num: int, block: Block, color: tuple[float, float, float] = (1, 0, 0),
                   width: float = 1, fontsize: float = 8):
        """
        Draw a box and text annotation for a single block on a specific page.

        Parameters
        ----------
        page_num : int
            The page number (0-indexed) to draw on.
        block : Block
            The Block object containing vertices and text.
        color : Tuple[float, float, float], optional
            The RGB color for the box and text (default is red).
        width : float, optional
            The width of the box outline (default is 1).
        fontsize : float, optional
            The font size for the text annotation (default is 8).
        """
        pdf_page = self.pdf_document[page_num]

        # Convert normalized coordinates to absolute coordinates
        x0, y0 = block.vertices[0]
        x1, y1 = block.vertices[2]
        rect = fitz.Rect(
            x0 * pdf_page.rect.width,
            y0 * pdf_page.rect.height,
            x1 * pdf_page.rect.width,
            y1 * pdf_page.rect.height
        )

        # Draw rectangle
        pdf_page.draw_rect(rect, color=color, width=width)

        # Add text annotation
        pdf_page.insert_text((rect.x0, rect.y0 - 5), block.text[:20] + "...", fontsize=fontsize, color=color)

    def annotate_document(self, parsed_document: ParsedDocument):
        """
        Annotate the entire document based on the parsed_document.

        Parameters
        ----------
        parsed_document : ParsedDocument
            The parsed document containing pages and blocks of text.
        """
        for page_num, page in enumerate(parsed_document.pages):
            for block in page.blocks:
                self.draw_block(page_num, block)

    def save_and_close(self, output_pdf_path: Path):
        self.pdf_document.save(output_pdf_path)
        self.pdf_document.close()


async def main():
    """
    Main function to process a PDF and create an annotated version.
    """
    # Process PDF into text blocks
    document_ai = DocumentParser()
    input_pdf_path = Path("data/inpatient_record.pdf")
    parsed_document = await document_ai.process_document(input_pdf_path)

    # Create annotated PDF -> annotator.draw_block(...) might be useful to you
    output_pdf_path = Path("data/output.pdf")
    annotator = PDFAnnotator(input_pdf_path)
    annotator.annotate_document(parsed_document)
    annotator.save_and_close(output_pdf_path)
    print(f"Annotated PDF saved to: {output_pdf_path}")


if __name__ == '__main__':
    asyncio.run(main())