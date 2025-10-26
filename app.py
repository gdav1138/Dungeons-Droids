from flask import Flask, request, jsonify, session, render_template
from hello import getInput, getOutput
import uuid

app = Flask(__name__)
app.secret_key = "dungeons_and_droids_key"

@app.route('/', methods = ["GET", "POST"])
def home():
    if "userId" not in session:
        session["userId"] = str(uuid.uuid4())
    
    response_text = getOutput(userId=session["userId"], userInput = None)
    return render_template("gameloop.html", response_text=response_text)

if __name__ == '__main__':
    app.run(debug=True)