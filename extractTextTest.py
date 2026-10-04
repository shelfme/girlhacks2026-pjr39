from pypdf import PdfReader
from flask import Flask, render_template, request
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
    data = json.loads(response.output_text)
    return data["flashcards"]

# flask
app = Flask(__name__, template_folder="templates")

@app.route("/", methods=["GET", "POST"])
def index():
    flashcards = []

    if request.method == "POST":
        notes = request.form.get("notes", "")
        uploaded_file = request.files.get("file")

        if uploaded_file and uploaded_file.filename:
            notes = uploaded_file.read().decode("utf-8")

        if notes.strip():
            flashcards = generate_flashcards(notes)

    print("Flashcards:")
    print(flashcards)

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


@app.route("/flashcards")
def flashcards_page():
    return render_template("flashcards.html")

if __name__ == "__main__":
    app.run(debug=True)