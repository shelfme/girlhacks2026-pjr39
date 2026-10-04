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

# flask
app = Flask(__name__, template_folder="templates")
app.secret_key = "dev-super-secret-key-of-secretness"

@app.route("/", methods=["GET", "POST"])
def index():

    flashcards = []

    if request.method == "POST":

        # from txt box
        notes = request.form.get("notes", "")

        # txt file upload
        uploaded_file = request.files.get("file")

        if uploaded_file and uploaded_file.filename:
            notes = uploaded_file.read().decode("utf-8")

        if notes.strip():
            print("sending notes to azure\n")
            flashcards = generate_flashcards(notes)

            print("got flashcards:", flashcards)

            # save generated cards temporarily
            print("got flashcards\n")
            session["flashcards"] = flashcards
        return redirect(url_for("index"))

    flashcards = session.pop("flashcards", [])
    
    # flashcards = generate_flashcards()

    print("Flashcards:")
    print(flashcards)

    # render template
    return render_template(
        "index3.html",
        flashcards=flashcards
    )

if __name__ == "__main__":
    app.run(debug=True)