from pypdf import PdfReader
from flask import Flask, render_template, request, redirect,url_for, session
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import os
import json

# azure
endpoint = "https://girlhacks-pjr39-resource.services.ai.azure.com/api/projects/girlhacks-pjr39"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

my_agent = "natha"
my_version = "5"

# get text from notes
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

# request from azure in formatted JSON
def generate_flashcards(notes):
    openai_client = project_client.get_openai_client()  
    response = openai_client.responses.create(
    input=[{"role": "user",
            "content": """
            Here are my study notes:\n\n,

            """ + notes + """

            Create an appropriate number of flashcards baesd on the
            amount and complexity of the notes provided.

            Short notes: 5-10 flashcards
            Medium notes: 10-20 flashcards
            Large notes: 20-40 flashcards
            Never create more than 40 flashcards.

            Cover the important concepts and avoid repetitive
            or unnecessary questions.

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

            Preferably, keep the answers
            to short and concise.
            
            """}],
    extra_body={"agent_reference": {"name": my_agent, "version": my_version, "type": "agent_reference"}},
    )
    data = json.loads(response.output_text)
    return data["flashcards"]

def generate_study_guide(notes):
    openai_client = project_client.get_openai_client()

    response = openai_client.responses.create(
        input=[{
            "role": "user",
            "content": """
Here are my study notes:

""" + notes + """

Create a study guide based only on these notes.

Return ONLY valid JSON in exactly this format:

{
    "main_topics": [
        "Topic 1",
        "Topic 2"
    ],
    "important_concepts": [
        "Important concept 1",
        "Important concept 2"
    ],
    "key_terms": [
        {
            "term": "Term 1",
            "definition": "Definition 1"
        },
        {
            "term": "Term 2",
            "definition": "Definition 2"
        }
    ],
    "important_facts": [
        "Important fact 1",
        "Important fact 2"
    ],
    "things_to_remember": [
        "Important thing 1",
        "Important thing 2"
    ]
}

Rules:
- Return only valid JSON.
- Do not use markdown.
- Do not include ```json.
- Use only information from the notes.
- Make the study guide clear and useful.
- Do not add unrelated information.
"""
        }],
        extra_body={
            "agent_reference": {
                "name": my_agent,
                "version": my_version,
                "type": "agent_reference"
            }
        },
    )

    data = json.loads(response.output_text)

    return data

# flask
app = Flask(__name__, template_folder="templates")
app.secret_key = "dev-super-secret-key-of-secretness"

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("home.html")


@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json()
    notes = data.get("notes", "")

    print("Received notes:")
    print(notes)

    flashcards = generate_flashcards(notes)

    print("Generated flashcards:")
    print(flashcards)

    return {"flashcards": flashcards}


@app.route("/study-guide", methods=["POST"])
def study_guide():
    data = request.get_json()

    notes = data.get("notes", "")

    guide = generate_study_guide(notes)

    return {"study_guide": guide}


@app.route("/flashcards")
def flashcards_page():
    return render_template("flashcards.html")

@app.route("/studyguide")
def studyguide_page():
    return render_template("studyguide.html")

if __name__ == "__main__":
    app.run(debug=True)