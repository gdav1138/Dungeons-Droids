# Main flask application. Handles sessions, routing, and OpenAI communication
from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from hello import getOutput
from user_db import register_user, authenticate_user, get_user_by_username
import uuid

# This file loads up Flask to serve web pages at the root / directory.
# Every time the client connects, it gets the variables from the web browser (input)
# and then calls the getOutput function in hello.py, which tracks the state of the game.
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
        result = getOutput(userId=session["userId"], userInput=userInput)
        return jsonify(result)

    # For first load:
    print("First load:")
    result = getOutput(userId=session["userId"], userInput="None")
    print("First response: " + str(result))
    username = session.get("username", "User")
    return render_template("gameloop.html", 
                         first_response=result.get("response"), 
                         first_map=result.get("map"),
                         first_minimap=result.get("minimap"),
                         first_inventory=result.get("inventory", []),
                         username=username)


if __name__ == '__main__':
    app.run(debug=True)
