# Main flask application. Handles sessions, routing, and OpenAI communication
from flask import Flask, request, jsonify, session, render_template, redirect, url_for, flash
from hello import getOutput, initializeStartUp
from user_db import register_user, authenticate_user, get_user_by_username
from all_global_vars import all_global_vars
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
        try:
            print("In POST")
            data = request.get_json(force=True)
            userInput = data.get("command", "").strip()
            response_text = getOutput(userId=session["userId"], userInput=userInput)
            player_char = all_global_vars.get_player_character(session["userId"])
            items_here = all_global_vars.get_player_character(session["userId"]).get_room_array().list_items()
            return jsonify({
                "response": response_text,
                "inventory": player_char.get_inventory(),
                "items_here": items_here,
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        # Include a fresh minimap with every response
        rooms = all_global_vars.get_player_character(session["userId"]).get_room_array()
        map_html = rooms.render_minimap()
        return jsonify({"response": response_text, "map": map_html})

    user_id = session.get("userId")
    username = session.get("username", "User")
    if user_id:
        if not all_global_vars.has_userId(user_id):
            initializeStartUp(user_id)

        first_response = getOutput(userId=session["userId"], userInput="None")
    else:
        first_response = "Please log in."

    return render_template(
        "gameloop.html",
        first_response=first_response,
        username=username,
        first_inventory=[]
    )
    user_id = session.get("userId")
    username = session.get("username", "User")
    if user_id:
        if not all_global_vars.has_userId(user_id):
            initializeStartUp(user_id)

        first_response = getOutput(userId=session["userId"], userInput="None")
        first_inventory = all_global_vars.get_player_character(user_id).get_inventory()
        first_items = all_global_vars.get_player_character(session["userId"]).get_room_array().list_items()
    else:
        first_response = "Please log in."
        first_inventory = []
        first_items = []

    return render_template(
        "gameloop.html",
        first_response=first_response,
        username=username,
        first_inventory=first_inventory,
        first_items=first_items,
    )


if __name__ == '__main__':
    app.run(debug=True)
