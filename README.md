# Inpatient LLM Document Parser
---
This project creates an LLM agent to extract important information about medical events from inpatient records. Valid records are PDF documents, from which text is extracted using Google's DocumentAI OCR service. The agent leverages Gemini (specifically, `gemini-1.5.pro`), Google's latest generation LLM, and the model's function calling capabilities to return a structured output from text. The output is a list of events that are described by a standard set of fields. The particular fields that the model is instructed to fill in are presented in the table below.

| Field | Description |
|--------|--------------|
| `date` | Date of patient encounter |
| `description` | A description of the kind of medical event, e.g. consultation |
| `medical_findings` | Important medical findings from the event|
| `diagnoses` | Diagnoses that are made during the event |
| `new_orders` | Orders for tests or treatments |
| `follow-up_actions` | Follow-up actions that are indicated |

These fields were chosen for demonstration purposes only. They can be tailored according to the information that is desired. 

## Setup
---
To install, navigate to the repositroy root, create a virtual environment, and run the command `pip install .` The few dependencies for the project are listed in the `pyproject.toml` file.

Running the program requires calls to Google's DocumentAI OCR service and Gemini API. Therefore, you need to create a `.env` file modelled after the provided `.env.example` file and set the variables.
* Instructions for setting up a GCP project with an OCR processor and setting the first four environment variables can be found in [this Loom](https://www.loom.com/share/4d4ee611b4504cb7977cb47a9fc0058c?sid=db01e5aa-e057-4fa1-af85-94090c7f0c9d).  
* Instructions for generating a Gemini API key are found in [in this Google document](https://ai.google.dev/gemini-api/docs/api-key). The `GOOGLE_API_KEY` should be set to this key.

To run the Document Parser on a inpatient record, execute the command 
```
python submission.py --path-to-case-pdf <path-to-case-pdf.pdf> --path-to-output-json <path-to-output.json>
```
This will first process the pdf with DocumentAI and then pass the extracted text to the Document Parser agent. If setup is successful, you should see log messages to track progress. The output of the Document Parser, which at the output path specified in the command, is a `json` object consisting of a list of events with the fields described above. An example inpatient record and the corresponding output are provided at `data/inpatient_record.pdf` and `data/parsed_inpatient_record.json` 

## Source files
---
| File | Description |
|------|--------------|
| `pdf.py` | Defines the `DocumentAI` class for processing pdfs with Google's DocumentAI OCR service |
| `agent.py` | Contains the `DocumentParser` class defining the LLM agent |
| `prompts.py` | Contains the prompt template for the Document Parser agent |
| `tools.py` | Defines the tool used by the Document Parser agent |


## Suggested improvements
---
* **Batch processing.** DocumentAI's online process request is limited to 15 pages per request, whereas our example inpatient record has 60 pages. We circumvented the issue by simply processing the pages one at a time, but this increases processing time and risks hitting rate limits for large documents. A more robust solution would be to utilize DocumentAI's batch process request, which requires uploading the documents to GCP.
* **Output validation - type checking.** Currrently, no type checking is imposed on the output. The date, for example, is not always returned by the LLM in the requested MM-DD-YYYY format. We can address this kind of error by implementing retry policies with Pydantic validation.
* **Output validation - accuracy.** The content of the output is not automatically checked for comprehensiveness or accuracy. We could, for example, experiment with a second LLM agent to review the output of the Document Parser against the original document, instructing the agent to fill in missing information and check for accuracy.
* **Document formatting and chunking.** In this demo, the entire text is passed to the LLM at once, with little regard to formatting. We ignore potentially useful, non-textual data that are returned by DocumentAI, such as the location of page elements. While we do feel the LLM benefits from having the context of the entire document, we could experiment with chunking the document to allow the LLM to focus on more specific parts of the text.  
* **Hyperparamter tuning** We used the default configuration of Gemini, but hyperparameters could be tuned to improve quality of the output.
* **Tailoring the output information.** Domain experts should be consulted to identify precisely the kind of information the is necessary to extract. Then the prompt and the data fields in the above table should be tuned accordingly.
* **Benchmarking other LLMs** Our solution is designed to work with Google's Gemini series. One could instead use a model-agnostic framework like Langchain in order to plug in other LLMs and compare their performance.
