# Main flask application. Handles sessions, routing, and OpenAI communication
from flask import Flask, request, jsonify, session, render_template
from hello import getOutput
import uuid

#What does this file do?
#It loads up flask to serve web pages at the root / directory.
#Every time the client connects, it gets the variables from the web browser() (input)
#and then calls the getOutput function in hello.py, which tracks the state of the game.
app = Flask(__name__)
app.secret_key = "dungeons_and_droids_key"

@app.route('/', methods=["GET", "POST"])
def home():
    if "userId" not in session:
        session["userId"] = str(uuid.uuid4())

    if request.method == "POST":
        print("In POST")
        data = request.get_json(force=True)
        userInput = data.get("command", "").strip()
        response_text = getOutput(userId=session["userId"], userInput=userInput)
        return jsonify({"response": response_text})

    # For first load:
    print("First load:")
    first_response = getOutput(userId=session["userId"], userInput="None")
    print("First response: " + first_response)
    return render_template("gameloop.html", first_response=first_response)

if __name__ == '__main__':
    app.run(debug=True)