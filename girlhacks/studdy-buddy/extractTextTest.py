from pypdf import PdfReader
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

def extract_text(filename):

    if filename.lower().endswith(".txt"):

        with open(filename, "r", encoding="utf-8") as f:
            return f.read()

    elif filename.lower().endswith(".pdf"):

        reader = PdfReader(filename)

        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        return text

    else:
        return ""

# azure
endpoint = "https://girlhacks-pjr39-resource.services.ai.azure.com/api/projects/girlhacks-pjr39"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

my_agent = "natha"
my_version = "5"

# notes
notes = extract_text("test_notes.txt")
print("i got the notes chat")
print(notes[:50] + "...")

# send to azure
openai_client = project_client.get_openai_client()

# request in formatted JSON
response = openai_client.responses.create(
    input=[{"role": "user",
            "content": """
            Here are my study notes:\n\n,

            """ + notes + """

            Create 10 flashcards using these notes.
            Return only valid JSON in the following format:

            {{
                "flashcards": [
                    {{
                        "question": "What is photosynthesis?",
                        "answer": "{answer}"
                    }},
                    {{ 
                        "question": "Where does photosynthesis occur?",
                        "answer": "{answer}"
                    }}
                ]
            }}

            Do not include markdown.
            Do not include ```json.
            Return only the JSON, no other text.

            Also the questions don't have to be exactly the same
            as the format, just make sure they are valid JSON and 
            have a question and answer. Preferably, keep the answers
            to short and concise.
            
            """}],
    extra_body={"agent_reference": {"name": my_agent, "version": my_version, "type": "agent_reference"}},
)

print(f"Response output: {response.output_text}")