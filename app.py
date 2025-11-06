# Main flask application. Handles sessions, routing, and OpenAI communication
from flask import Flask, request, jsonify, session, render_template
from hello import getOutput
import uuid
from all_global_vars import all_global_vars

# What does this file do?
# It loads up flask to serve web pages at the root / directory.
# Every time the client connects, it gets the variables from the browser
# (input)
# and then calls the getOutput function in hello.py, which tracks game state.
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
        response_text = getOutput(
            userId=session["userId"], userInput=userInput
        )
        # Include a fresh minimap with every response
        rooms = all_global_vars.get_room_holder(session["userId"])
        map_html = rooms.render_minimap()
        return jsonify({"response": response_text, "map": map_html})

    # For first load:
    print("First load:")
    first_response = getOutput(userId=session["userId"], userInput="None")
    print("First response: " + first_response)
    rooms = all_global_vars.get_room_holder(session["userId"])
    first_map = rooms.render_minimap()
    return render_template(
        "gameloop.html", first_response=first_response, first_map=first_map
    )


if __name__ == '__main__':
    app.run(debug=True)
