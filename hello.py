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
from player_character import player_character
import os
from room import room_holder, Room

def initializeStartUp(userId):
    user_doc = user_db.get_user_by_id(userId)

    if user_doc["_player_character_id"] is None:
        print("No character set for current user. Creating Character...")

        # Generate Player
        all_global_vars.create_player(userId)
        # character = player_character()
        # all_global_vars.create_player(userId)
        # Initialize character with default values
        # character._level = 0
        # character._exp = 0
        # character._health = 100
        # character_id = character.store_player_character(character)   # Store character and get character_id

        # Generate Character
        character = player_character()
        all_global_vars.set_player_character(userId, character)

        character_id = character.store_player_character()  # Store character and get character_id
        user_db.update_user(userId, {"_player_character_id": character_id})  # Update user with character_id

        # Update section
        all_global_vars.set_section(userId, character.get_section())

    else:
        user_doc = user_db.get_user_by_id(userId)
        character_id = user_doc.get("_player_character_id")
        print(user_doc)
        returning_character = player_character.rehydrate_char(character_id)
        print(all_global_vars)
        all_global_vars.create_player(userId)
        all_global_vars.rehydrate_globals(userId, user_doc, returning_character)
        all_global_vars.get_room_holder(userId).get_full_description(userId)
        print(all_global_vars.get_room_holder(userId))

def doSectionStarting(userId):
    """Introduction section of the game where instructions are given to ChatGPT to greet the player, ask for their name, and set the era."""

    print("Starting up doSectionStarting with userID: " + str(userId))

    client_response = ""
    client_response += call_ai(
        "Greet the player as our new Text Game With AI Called Dungeons and Droids. Don't give any instructions to the user." )
    client_response += "<BR>"
    all_global_vars.get_theme(userId)._era = call_ai(
        "Pick an theme for this game to take place in. Make the answer very short, just a word or two, like medieval or sci-fi, but be creative")

    client_response += "This game takes place in the " + all_global_vars.get_theme(userId)._era + " era. <BR>"
    client_response += "What should we call your character?<BR>"
    all_global_vars.set_section(userId=userId, section="GetPlayerName")
    return client_response

def doGetPlayerName(userInput, userId):
    """Handles player name input. Stores it in player_character object."""
    client_response = ""
    new_name = userInput.strip()

    if not new_name:
        return "Please enter a valid name.<BR>"

    all_global_vars.get_player_character(userId).set_name(new_name)

    # Update character with new_name in database
    current_user = user_db.get_user_by_id(userId)
    if current_user and current_user.get("_player_character_id"):
        character_id = current_user["_player_character_id"]
        all_global_vars.get_player_character(userId).update_char(character_id, {"name": new_name})

    # Move to stat allocation - start with strength
    all_global_vars.set_section(userId, "GetPlayerStrength")
    return "Welcome, " + new_name + "!<BR><BR>You have 10 stat points to allocate between Strength and Intelligence.<BR>Enter your <strong>Strength</strong>:<BR>"

def doGetPlayerStrength(userInput, userId):
    """Handles strength input. Stores it and moves to intelligence input."""
    try:
        strength = int(userInput.strip())

        # Validate strength
        if strength < 0:
            return "Strength cannot be negative. Please enter a number between 0 and 10.<BR>"

        if strength > 10:
            return "Strength cannot exceed 10. Please enter a number between 0 and 10.<BR>"

        # Store strength temporarily in the character object
        character = all_global_vars.get_player_character(userId)
        character._str = strength

        # Calculate remaining points
        remaining_points = 10 - strength

        # Move to intelligence input
        all_global_vars.set_section(userId, "GetPlayerIntelligence")
        return f"Strength set to {strength}.<BR>You have {remaining_points} points remaining.<BR>Enter your <strong>Intelligence</strong>:<BR>"

    except ValueError:
        return "Please enter a valid number for Strength (0-10).<BR>"
    except Exception as e:
        return f"An error occurred: {str(e)}<BR>Please try again.<BR>"

def doGetPlayerIntelligence(userInput, userId):
    """Handles intelligence input. Validates total equals 10 and moves to confirmation."""
    try:
        intelligence = int(userInput.strip())

        # Get strength that was set in previous step
        character = all_global_vars.get_player_character(userId)
        strength = character._str

        # Validate intelligence
        if intelligence < 0:
            return f"Intelligence cannot be negative. Please enter a number between 0 and {10 - strength}.<BR>"

        # Check if total equals 10
        if strength + intelligence != 10:
            # Reprompt both strength and intelligence
            all_global_vars.set_section(userId, "GetPlayerStrength")
            return f"Error: Strength ({strength}) + Intelligence ({intelligence}) = {strength + intelligence} points.<BR>You must allocate exactly 10 points!<BR><BR>Please enter your stats again.<BR>Enter your <strong>Strength</strong>:<BR>"

        # Set intelligence on character temporarily
        character._int = intelligence

        # Move to confirmation step
        all_global_vars.set_section(userId, "ConfirmPlayerStats")
        return f"Your stat allocation:<BR>Strength: {strength}<BR>Intelligence: {intelligence}<BR>Total: {strength + intelligence} points<BR><BR>Type <strong>yes</strong> to confirm, or <strong>no</strong> to change your stats:<BR>"

    except ValueError:
        remaining = 10 - all_global_vars.get_player_character(userId)._str
        return f"Please enter a valid number for Intelligence.<BR>"
    except Exception as e:
        return f"An error occurred: {str(e)}<BR>Please try again.<BR>"

def doConfirmPlayerStats(userInput, userId):
    """Handles confirmation of stat allocation. Completes character creation or reprompts stats."""
    confirmation = userInput.strip().lower()

    if confirmation in ['yes', 'y']:
        # User confirmed - create character
        character = all_global_vars.get_player_character(userId)
        strength = character._str
        intelligence = character._int

        # Set final stats on character
        # character._level = 0  # Starting at level 0
        # character._exp = 0  # Starting experience points
        # character._health = 100  # Starting HP

        # Generate rooms and start main game loop
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

        cur_room = rooms.get_room(0, 0)
        cur_room.generate_description(userId)

        # Update character in database
        current_user = user_db.get_user_by_id(userId)
        if current_user and current_user.get("_player_character_id"):
            character_id = current_user["_player_character_id"]
            character.update_char(character_id, {
                "str": strength,
                "int": intelligence,
                "section": "MainGameLoop",
                "rooms_visited": rooms.to_dict(),
            })

        all_global_vars.set_section(userId, "MainGameLoop")

        client_response = ""
        client_response += f"Character created!<BR>"
        client_response += f"Strength: {strength}<BR>"
        client_response += f"Intelligence: {intelligence}<BR>"
        client_response += f"Level: 1<BR>"
        client_response += f"HP: 100<BR>"
        client_response += f"Experience: 0<BR><BR>"
        client_response += rooms.get_full_description(userId)

        return client_response

    elif confirmation in ['no', 'n']:
        # User wants to change stats - reprompt both
        all_global_vars.set_section(userId, "GetPlayerStrength")
        return "Please enter your stats again.<BR>Enter your <strong>Strength</strong>:<BR>"

    else:
        # Invalid input - ask again
        return "Please type <strong>yes</strong> to confirm your stats, or <strong>no</strong> to change them:<BR>"

def getInput():
    return input()

def getOutput(userInput, userId):

    while True:
        cur_section = all_global_vars.get_section(userId)
        if cur_section == "Starting":
            print("Calling doStarting")
            return doSectionStarting(userId)
        if cur_section == "GetPlayerName":
            print("Calling getplayerName")
            return doGetPlayerName(userInput, userId)
        if cur_section == "GetPlayerStrength":
            print("Calling getPlayerStrength")
            return doGetPlayerStrength(userInput, userId)
        if cur_section == "GetPlayerIntelligence":
            print("Calling getPlayerIntelligence")
            return doGetPlayerIntelligence(userInput, userId)
        if cur_section == "ConfirmPlayerStats":
            print("Calling confirmPlayerStats")
            return doConfirmPlayerStats(userInput, userId)
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
    