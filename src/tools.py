import google.generativeai as genai

# Parameters for the function call

event = genai.protos.Schema(
    type=genai.protos.Type.OBJECT,
    properties={
        "date": genai.protos.Schema(type=genai.protos.Type.STRING),
        "description": genai.protos.Schema(type=genai.protos.Type.STRING),
        "medical_findings": genai.protos.Schema(type=genai.protos.Type.STRING),
        "diagnoses": genai.protos.Schema(type=genai.protos.Type.STRING),
        "new_orders": genai.protos.Schema(type=genai.protos.Type.STRING),
        "follow_up_actions": genai.protos.Schema(
            type=genai.protos.Type.STRING
        ),
    },
    required=[
        "date",
        "description",
        "medical_findings",
        "diagnoses",
        "new_orders",
        "follow_up_actions",
    ],
)

events = genai.protos.Schema(type=genai.protos.Type.ARRAY, items=event)

# Tool for DocumentParser agent

add_to_database = genai.protos.FunctionDeclaration(
    name="add_to_database",
    description="Inserts entries into the database.",
    parameters=genai.protos.Schema(
        type=genai.protos.Type.OBJECT, properties={"events": events}
    ),
)
