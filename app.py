# Main flask application. Currently handles user sessions, routing, and communication    #
# between the web interface OpenAI API                                                   #
from flask import Flask, request, jsonify, session, render_template, redirect
from hello import getInput, getOutput
import uuid

app = Flask(__name__)
app.secret_key = "dungeons_and_droids_key"

@app.route('/', methods = ["GET", "POST"])
def home():
    """Main route to handle Flask implementation. Assigns the user with a unique session-ID"""
    print("Calling Home")
    userInput = None

    # Create new session ID if the user is new
    if "userId" not in session:
        print("UserId Not in Session")
        session["userId"] = str(uuid.uuid4())
        userInput = "None"
    else:
        print("UserID in session")
        userInput = request.form.get("command")
        
        if userInput is None:
            userInput = request.args.get("command")
            if userInput is None:
                print("Error: Couldn't read userInput, it's none")
                session.clear()
                return "Error, couldn't read userInput, it's none. Resetting."
        
    if userInput is None:
        print("GET, Calling getOutput with userInput = <NONE>")
    else:
        print("GET, Calling getOutput with userInput = " + userInput)
    response_text = getOutput(userId=session["userId"], userInput = userInput)
    print("Calling render template with response: " + response_text)
    return render_template("gameloop.html", response_text=response_text)

if __name__ == '__main__':
    app.run(debug=True)
    