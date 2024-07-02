import argparse
import json
import logging
from pathlib import Path

from agents import DocumentParser
from pdf import DocumentAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main(input_file_path: Path, output_file_path: Path) -> None:
    """Write the entrypoint to your submission here"""

    # Process pdf to extract text
    document_ai = DocumentAI()
    document = document_ai(input_file_path)

    # Parse text with LLM agent
    document_parser = DocumentParser()
    parsed_info = document_parser(document)

    # Save output
    with open(output_file_path, "w") as f:
        json.dump(parsed_info, f, indent=4)

    logger.info(f"Parsed ouput saved to {output_file_path}")

    logger.info(parsed_info)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path-to-case-pdf",
        metavar="path",
        type=str,
        help="Path to local test case with which to run your code",
    )
    parser.add_argument(
        "--path-to-output-json",
        metavar="path",
        type=str,
        help="Path to file to save output",
    )  
    args = parser.parse_args()
    main(Path(args.path_to_case_pdf), Path(args.path_to_output_json))
