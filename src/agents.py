import dotenv
import logging
import os
from typing import Dict, List

import google.generativeai as genai

from prompts import PARSER_PROMPT_TEMPLATE
from tools import add_to_database

dotenv.load_dotenv()

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-1.5-pro"

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)


class DocumentParser:
    """LLM agent for parsing important medical event information from
    inpatient record."""

    def __init__(self) -> None:

        self.prompt_template = PARSER_PROMPT_TEMPLATE
        self.tools = [add_to_database]
        self.model = genai.GenerativeModel(
            model_name=MODEL_NAME, tools=self.tools
        )

    def generate_content(self, text) -> genai.types.GenerateContentResponse:
        """Thin wrapper around Google generate_content model method."""

        logger.info(f"Calling {MODEL_NAME} to generate response")

        prompt = self.prompt_template.format(record=text)
        response = self.model.generate_content(
            prompt, tool_config={"function_calling_config": "ANY"}
        )  # Force function call

        logger.info(f"Received response from {MODEL_NAME}")

        return response

    def __call__(self, text: str) -> List[Dict[str, str]]:
        """Parses medical event information from text and structures output
        as json object."""

        response = self.generate_content(text)
        function_call = response.candidates[0].content.parts[0].function_call
        output_dict = type(function_call).to_dict(function_call)["args"][
            "events"
        ]

        return output_dict


if __name__ == "__main__":

    # Example usage
    text = """Date: 07/01/2024, patient presented to hospital and was
    diagnosed a cold."""

    document_parser = DocumentParser()
    output = document_parser(text)