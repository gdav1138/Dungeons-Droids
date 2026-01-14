# Main game logic file. Handles interactions between player inputs and OpenAI responses  #
# The key part of this file is the all_global_vars. That saves each players variables, associated with
# a userId. Since each web request is separate, it has to remember where in the program it is,
# which is the section portion, with get_section and set_section to say where in the program that user
# is. There's also a mainloop section that leads to another file.
from openai import OpenAI
from dotenv import load_dotenv
from all_global_vars import all_global_vars
from open_ai_api import call_ai
from main_loop import do_main_loop
from bson.objectid import ObjectId
import user_db
import character_db
import os
from room import room_holder, Room


def doSectionStarting(userId):
    """Introduction section of the game where instructions are given to ChatGPT to greet the player, ask for their name, and set the era."""

    print("Starting up doSectionStarting with userID: " + str(userId))

    client_response = ""
    client_response += call_ai(
        "Greet the player as our new Text Game With AI Called Dungeons and Droids. Don't give any instructions to the user." )
    client_response += "<BR>"
    all_global_vars.get_theme(userId)._era = call_ai(
        "Pick an theme for this game to take place in. Make the answer very short, just a word or two, like medieval or sci-fi, try and go fast.")

    client_response += "This game takes place in the " + all_global_vars.get_theme(userId)._era + " era. <BR>"
    client_response += "What should we call your character?<BR>"
    all_global_vars.set_section(userId=userId, section="GetPlayerName")
    return client_response

def doGetPlayerName(userInput, userId):
    """Handles player name input. Stores it in player_character object, and generates a themed location using OpenAI API"""
    import random
    
    client_response = ""
    new_name = userInput
    all_global_vars.get_player_character(userId).set_name(new_name)

    rooms = all_global_vars.get_room_holder(userId)
    
    # Generate a maze of rooms with a clear path
    # Create a simple branching dungeon structure
    rooms.add_empty_room(0, 0)  # Starting room
    rooms.add_empty_room(0, 1)  # North
    rooms.add_empty_room(1, 1)  # East from north
    rooms.add_empty_room(0, 2)  # North again
    rooms.add_empty_room(1, 0)  # East from start
    rooms.add_empty_room(2, 0)  # East again
    rooms.add_empty_room(2, 1)  # North from east path
    
    cur_room = rooms.get_room(0,0)

    # Update character with new_name
    current_user = user_db.get_user_by_id(userId)
    character_id = current_user["_player_character_id"]
    character_db.update_char(character_id, {"name": new_name})

    cur_room.generate_description(userId)
    
    all_global_vars.set_section(userId, "MainGameLoop")
    return rooms.get_full_description(userId)

def getInput():
    return input()

def getOutput(userInput, userId):
    
    while True:
        if userId not in all_global_vars._userIdList:
            print("UserID not in userIdList")

            # Generate Player
            all_global_vars.create_player(userId)
            user_db.create_user(userId)   # Store user_id in MongoDB
            character = all_global_vars.get_player_character(userId)
            character_id = character_db.store_player_character(character)   # Store character and get character_id
            user_db.update_user(userId, {"_player_character_id": character_id})   # Update user with character_id

            # Update section
            all_global_vars.set_section(userId, "Starting")
        cur_section = all_global_vars.get_section(userId)
        if cur_section == "Starting":
            print("Calling doStarting")
            return doSectionStarting(userId)
        if cur_section == "GetPlayerName":
            print("Calling getplayerName")
            return doGetPlayerName(userInput, userId)
        if cur_section == "MainGameLoop":
            return do_main_loop(userInput, userId)
        if cur_section == "Restart":
            all_global_vars._userIdList.pop(userId)
        

def main():
    userInput = ""
    while True:
        print(getOutput(userInput, userId = 1))
        userInput = getInput()

if __name__ == "__main__":
    main()
    