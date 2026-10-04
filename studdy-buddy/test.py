from flask import Flask, render_template, request
from pypdf import PdfReader
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
import os

app = Flask(__name__)

# Azure setup
endpoint = "https://girlhacks-pjr39-resource.services.ai.azure.com/api/projects/girlhacks-pjr39"

project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

my_agent = "natha"
my_version = "4"


# Extract text from file
def extract_text(file):

    filename = file.filename.lower()

    # if filename.endswith(".txt"):
    #     return file.read().decode("utf-8")

    if filename.lower().endswith(".txt"):
        with open(file, "r", encoding="utf-8") as f:
            return f.read()

    elif filename.endswith(".pdf"):

        reader = PdfReader(file)

        text = ""

        for page in reader.pages:
            text += page.extract_text() or ""

        return text

    else:
        return ""

# testing with sample file
notes = extract_text("test_notes.txt")
print(notes)

# Flask route
@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        file = request.files["notes"]

        print("Uploaded:", file.filename)

        notes = extract_text(file)

        print("Extracted text:")
        print(notes[:1000])

        return "Successfully extracted your notes!"

    return render_template("index.html")


# Start server
if __name__ == "__main__":
    app.run(debug=True)