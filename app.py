<<<<<<< Updated upstream
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
    
=======
# Main flask application. Handles sessions, routing, and OpenAI communication
from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from hello import getOutput
from user_db import register_user, authenticate_user, get_user_by_username
import uuid

#What does this file do?
#It loads up flask to serve web pages at the root / directory.
#Every time the client connects, it gets the variables from the web browser() (input)
#and then calls the getOutput function in hello.py, which tracks the state of the game.
app = Flask(__name__)
app.secret_key = "dungeons_and_droids_key"


@app.route('/login', methods=["GET", "POST"])
def login():
    """Login page - handles both GET (display form) and POST (process login)"""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not username or not password:
            flash("Please provide both username and password", "error")
            return render_template("login.html")
        
        user_id = authenticate_user(username, password)
        if user_id:
            session["userId"] = user_id
            session["username"] = username
            flash("Login successful!", "success")
            return redirect(url_for("home"))
        else:
            flash("Invalid username or password", "error")
            return render_template("login.html")
    
    # If already logged in, redirect to home
    if "userId" in session:
        return redirect(url_for("home"))
    
    return render_template("login.html")


@app.route('/register', methods=["POST"])
def register():
    """Handle user registration"""
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    
    if not username or not password:
        flash("Please provide both username and password", "error")
        return render_template("login.html")
    
    if len(password) < 4:
        flash("Password must be at least 4 characters long", "error")
        return render_template("login.html")
    
    user_id = register_user(username, password)
    if user_id:
        session["userId"] = user_id
        session["username"] = username
        flash("Account created successfully!", "success")
        return redirect(url_for("home"))
    else:
        flash("Username already exists. Please choose a different username.", "error")
        return render_template("login.html")


@app.route('/logout')
def logout():
    """Logout user and clear session"""
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("login"))


@app.route('/', methods=["GET", "POST"])
def home():
    # Check authentication for both GET and POST
    if "userId" not in session:
        if request.method == "POST":
            return jsonify({"error": "Not authenticated"}), 401
        return redirect(url_for("login"))
    
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
    username = session.get("username", "User")
    return render_template("gameloop.html", first_response=first_response, username=username)


if __name__ == '__main__':
    app.run(debug=True)
>>>>>>> Stashed changes
