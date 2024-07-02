PARSER_PROMPT_TEMPLATE = """
The following is the medical record of an inpatient at a hospital.
The record may consist of several distinct documents corresponding to
different events during a patient's stay, such as a consultation by a medical
professional, a diagnostic test, or administration of a therapy. In order to
make an insurance claim, we need to extract detailed information about each
event for our database, including
* the date of the event, in MM-DD-YYYY format;
* a description of the event;
* all medical findings from the event;
* diagnoses from the event, if any are made;
* new orders for tests or treatments, if any are made;
* follow-up actions, if any are recommended.
Please ignore all medical history that is not immediately applicable to the
present case. Also note that the record may not be in chronological order and
some information may be repeated across multiple pages. Here is the patient's
record: 
{record}
"""
