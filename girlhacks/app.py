from flask import Flask, render_template, request
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient

# establishing endpoint and project client
endpoint = "https://girlhacks-pjr39-resource.services.ai.azure.com/api/projects/girlhacks-pjr39"
project_client = AIProjectClient(
    endpoint=endpoint,
    credential=DefaultAzureCredential(),
)

# agent and version
my_agent = "natha"
my_version = "5"

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        file = request.files["notes"]
        print("User uploaded:", file.filename)
        return "Got your notes!"
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)

notes = extract_text(file)  # make function

thread = project_client.agents.threads.create()

project_client.agents.messages.create(
    thread_id=thread.id,
    role="user",
    content=f"""
Here are my study notes:

{notes}

Create flashcards from these notes.
"""
)

run = project_client.agents.runs.create_and_process(
    thread_id=thread.id,
    agent_id=my_agent,
    agent_version=my_version
)