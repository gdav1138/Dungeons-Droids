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

        # Generate Character
        all_global_vars.create_player(userId)
        character = player_character()
        all_global_vars.set_player_character(userId, character)

        character_id = character.store_player_character()  # Store character and get character_id
        user_db.update_user(userId, {"_player_character_id": character_id})  # Update user with character_id

        # Print Game Version
        print(f"<strong>{all_global_vars.get_version(userId)}</strong><BR><BR>")

        # Update section
        all_global_vars.set_section(userId, character.get_section())

    # If user already has a character, load it
    else:
        user_doc = user_db.get_user_by_id(userId)
        character_id = user_doc.get("_player_character_id")

        # Reinitialize player_character object for function use
        returning_character = player_character.rehydrate_char(character_id)

        # Reinitialize global container and load it with the rehydrated character
        all_global_vars.create_player(userId)
        all_global_vars.rehydrate_globals(userId, user_doc, returning_character)

        all_global_vars.get_room_holder(userId).get_full_description(userId)


def doSectionStarting(userId):
    """Introduction section of the game where instructions are given to ChatGPT to greet the player,
    ask for their name, and set the era."""

    print("Starting up doSectionStarting with userID: " + str(userId))

    # Print Game Version
    print(f"<strong>{all_global_vars.get_version(userId)}</strong><BR><BR>")

    client_response = ""

    client_response += call_ai(
        "Greet the player as our new Text Game With AI Called Dungeons and Droids. "
        "Don't give any instructions to the user."
    )
    client_response += "<BR>"

    new_theme = call_ai(
        "Pick an theme for this game to take place in. Make the answer very short, "
        "just a word or two, like medieval or sci-fi, but be creative"
    )

    client_response += "This game takes place in the " + new_theme + " era. <BR>"
    client_response += "What should we call your character?<BR>"

    all_global_vars.get_player_character(userId).set_section(section="GetPlayerName")
    all_global_vars.get_player_character(userId).set_theme(new_theme)

    return client_response


def doGetPlayerName(userInput, userId):
    """Handles player name input. Stores it in player_character object."""

    client_response = ""
    new_name = userInput.strip()

    if not new_name:
        return "Please enter a valid name.<BR>"

    # Update character name
    all_global_vars.get_player_character(userId).set_name(new_name)

    # Update character with new_name in database
    current_user = user_db.get_user_by_id(userId)
    if current_user and current_user.get("_player_character_id"):
        character_id = current_user["_player_character_id"]
        all_global_vars.get_player_character(userId).update_char(character_id, {"name": new_name})

    # Move to appearance customization
    all_global_vars.get_player_character(userId).set_section(section="GetPlayerPronouns")
    return ("Welcome, " + new_name
            + "!<BR><BR>Before stats, let's customize your character."
              "<BR>What pronouns should NPCs use for you? (examples: they/them, she/her, he/him, or type 'skip')<BR>")


def doGetPlayerPronouns(userInput, userId):
    """Optional pronouns field, then move to appearance summary."""
    pronouns = (userInput or "").strip()
    character = all_global_vars.get_player_character(userId)
    if pronouns and pronouns.lower() != "skip":
        character.set_pronouns(pronouns)

        current_user = user_db.get_user_by_id(userId)
        if current_user and current_user.get("_player_character_id"):
            character_id = current_user["_player_character_id"]
            character.update_char(character_id, {"appearance.pronouns": pronouns})

    all_global_vars.get_player_character(userId).set_section(section="GetPlayerAppearance")
    return ("In one sentence, describe your character's appearance (hair/eyes/outfit/anything you want)."
            "<BR>(Or type 'skip')<BR>")


def doGetPlayerAppearance(userInput, userId):
    """Freeform appearance summary stored on character, then start stat allocation."""
    summary = (userInput or "").strip()
    character = all_global_vars.get_player_character(userId)
    if summary and summary.lower() != "skip":
        character.set_appearance_summary(summary)

        current_user = user_db.get_user_by_id(userId)
        if current_user and current_user.get("_player_character_id"):
            character_id = current_user["_player_character_id"]
            character.update_char(character_id, {"appearance.summary": summary})

    all_global_vars.get_player_character(userId).set_section(section="GetPlayerStrength")
    return ("Great. Now for stats.<BR><BR>"
            "You have <strong>20</strong> stat points to allocate across "
            "<strong>Strength, Intelligence, Dexterity, Charisma, Wisdom, Constitution</strong>."
            "<BR>Each stat must be between 0 and 10, and the total must equal 20."
            "<BR><BR>Enter your <strong>Strength</strong>:<BR>")


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
        remaining_points = 20 - strength

        # Move to intelligence input
        all_global_vars.get_player_character(userId).set_section(section="GetPlayerIntelligence")
        return (f"Strength set to {strength}.<BR>You have {remaining_points} points remaining."
                f"<BR>Enter your <strong>Intelligence</strong>:<BR>")

    except ValueError:
        return "Please enter a valid number for Strength (0-10).<BR>"
    except Exception as e:
        return f"An error occurred: {str(e)}<BR>Please try again.<BR>"


def doGetPlayerIntelligence(userInput, userId):
    """Handles intelligence input. Then moves to dexterity."""
    try:
        intelligence = int(userInput.strip())

        character = all_global_vars.get_player_character(userId)
        strength = character._str

        if intelligence < 0 or intelligence > 10:
            return "Intelligence must be between 0 and 10.<BR>"

        character._int = intelligence

        running_total = strength + intelligence
        if running_total > 20:
            all_global_vars.get_player_character(userId).set_section(section="GetPlayerStrength")
            return (f"Error: Strength ({strength}) + Intelligence ({intelligence}) exceeds 20 points."
                    "<BR><BR>Please enter your stats again.<BR>Enter your <strong>Strength</strong>:<BR>")

        remaining = 20 - running_total
        all_global_vars.get_player_character(userId).set_section(section="GetPlayerDexterity")
        return (f"Intelligence set to {intelligence}.<BR>You have {remaining} points remaining."
                f"<BR>Enter your <strong>Dexterity</strong>:<BR>")
    except ValueError:
        return "Please enter a valid number for Intelligence.<BR>"
    except Exception as e:
        return f"An error occurred: {str(e)}<BR>Please try again.<BR>"


def doGetPlayerDexterity(userInput, userId):
    """Handles dexterity input. Then moves to charisma."""
    try:
        dex = int(userInput.strip())
        if dex < 0 or dex > 10:
            return "Dexterity must be between 0 and 10.<BR>"

        character = all_global_vars.get_player_character(userId)
        character._dex = dex

        running_total = character._str + character._int + dex
        if running_total > 20:
            all_global_vars.get_player_character(userId).set_section(section="GetPlayerStrength")
            return ("Error: Your stats exceed 20 points."
                    "<BR><BR>Please enter your stats again.<BR>Enter your <strong>Strength</strong>:<BR>")

        remaining = 20 - running_total
        all_global_vars.get_player_character(userId).set_section(section="GetPlayerCharisma")
        return (f"Dexterity set to {dex}.<BR>You have {remaining} points remaining."
                f"<BR>Enter your <strong>Charisma</strong>:<BR>")
    except ValueError:
        return "Please enter a valid number for Dexterity.<BR>"
    except Exception as e:
        return f"An error occurred: {str(e)}<BR>Please try again.<BR>"


def doGetPlayerCharisma(userInput, userId):
    """Handles charisma input. Then moves to wisdom."""
    try:
        cha = int(userInput.strip())
        if cha < 0 or cha > 10:
            return "Charisma must be between 0 and 10.<BR>"

        character = all_global_vars.get_player_character(userId)
        character._cha = cha

        running_total = character._str + character._int + character._dex + cha
        if running_total > 20:
            all_global_vars.get_player_character(userId).set_section(section="GetPlayerStrength")
            return ("Error: Your stats exceed 20 points."
                    "<BR><BR>Please enter your stats again.<BR>Enter your <strong>Strength</strong>:<BR>")

        remaining = 20 - running_total
        all_global_vars.get_player_character(userId).set_section(section="GetPlayerWisdom")
        return (f"Charisma set to {cha}.<BR>You have {remaining} points remaining."
                f"<BR>Enter your <strong>Wisdom</strong>:<BR>")
    except ValueError:
        return "Please enter a valid number for Charisma.<BR>"
    except Exception as e:
        return f"An error occurred: {str(e)}<BR>Please try again.<BR>"


def doGetPlayerWisdom(userInput, userId):
    """Handles wisdom input. Then moves to constitution."""
    try:
        wis = int(userInput.strip())
        if wis < 0 or wis > 10:
            return "Wisdom must be between 0 and 10.<BR>"

        character = all_global_vars.get_player_character(userId)
        character._wis = wis

        running_total = character._str + character._int + character._dex + character._cha + wis
        if running_total > 20:
            all_global_vars.get_player_character(userId).set_section(section="GetPlayerStrength")
            return ("Error: Your stats exceed 20 points."
                    "<BR><BR>Please enter your stats again.<BR>Enter your <strong>Strength</strong>:<BR>")

        remaining = 20 - running_total
        all_global_vars.get_player_character(userId).set_section(section="GetPlayerConstitution")
        return (f"Wisdom set to {wis}.<BR>You have {remaining} points remaining."
                f"<BR>Enter your <strong>Constitution</strong>:<BR>")
    except ValueError:
        return "Please enter a valid number for Wisdom.<BR>"
    except Exception as e:
        return f"An error occurred: {str(e)}<BR>Please try again.<BR>"


def doGetPlayerConstitution(userInput, userId):
    """Handles constitution input, validates total == 20, then confirmation."""
    try:
        con = int(userInput.strip())
        if con < 0 or con > 10:
            return "Constitution must be between 0 and 10.<BR>"

        character = all_global_vars.get_player_character(userId)
        character._con = con

        total = (
            character._str + character._int + character._dex +
            character._cha + character._wis + con
        )
        if total != 20:
            all_global_vars.get_player_character(userId).set_section(section="GetPlayerStrength")
            return (f"Error: Your total is {total} points. You must allocate exactly 20."
                    "<BR><BR>Please enter your stats again.<BR>Enter your <strong>Strength</strong>:<BR>")

        all_global_vars.get_player_character(userId).set_section(section="ConfirmPlayerStats")
        return (f"Your stat allocation:<BR>"
                f"Strength: {character._str}<BR>"
                f"Intelligence: {character._int}<BR>"
                f"Dexterity: {character._dex}<BR>"
                f"Charisma: {character._cha}<BR>"
                f"Wisdom: {character._wis}<BR>"
                f"Constitution: {character._con}<BR>"
                f"Total: {total} points<BR><BR>"
                f"Type <strong>yes</strong> to confirm, or <strong>no</strong> to change your stats:<BR>")
    except ValueError:
        return "Please enter a valid number for Constitution.<BR>"
    except Exception as e:
        return f"An error occurred: {str(e)}<BR>Please try again.<BR>"


def doConfirmPlayerStats(userInput, userId):
    """Handles confirmation of stat allocation. Completes character creation or reprompts stats."""
    confirmation = userInput.strip().lower()

    if confirmation in ['yes', 'y']:
        # User confirmed
        # Generate rooms and start main game loop
        rooms = all_global_vars.get_player_character(userId).get_room_array()

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

        # Update player state for session
        all_global_vars.get_player_character(userId).set_section(section="MainGameLoop")

        # Update character in database
        current_user = user_db.get_user_by_id(userId)
        if current_user and current_user.get("_player_character_id"):
            character_id = current_user["_player_character_id"]
            character = all_global_vars.get_player_character(userId)
            character.update_player_character(character_id)

        client_response = ""
        client_response += f"Character created!<BR>"
        client_response += f"Level: 1<BR>"
        client_response += f"HP: 100<BR>"
        client_response += f"Experience: 0<BR><BR>"
        client_response += rooms.get_full_description(userId)

        return client_response

    elif confirmation in ['no', 'n']:
        # User wants to change stats - reprompt both
        all_global_vars.get_player_character(userId).set_section(section="GetPlayerStrength")
        return "Please enter your stats again.<BR>Enter your <strong>Strength</strong>:<BR>"

    else:
        # Invalid input - ask again
        return "Please type <strong>yes</strong> to confirm your stats, or <strong>no</strong> to change them:<BR>"


def getInput():
    return input()

def restart_game(userId):
    user_doc = user_db.get_user_by_id(userId)
    old_char_id = user_doc.get("_player_character_id")
    player_character.delete_character(old_char_id)
    user_db.update_user(userId, {"_player_character_id": None})
    all_global_vars._userIdList.pop(userId, None)
    initializeStartUp(userId)
    return doSectionStarting(userId)

def getOutput(userInput, userId):

    while True:
        cur_section = all_global_vars.get_player_character(userId).get_section()
        if cur_section == "Starting":
            print("Calling doStarting")
            return doSectionStarting(userId)
        if cur_section == "GetPlayerName":
            print("Calling getplayerName")
            return doGetPlayerName(userInput, userId)
        if cur_section == "GetPlayerPronouns":
            return doGetPlayerPronouns(userInput, userId)
        if cur_section == "GetPlayerAppearance":
            return doGetPlayerAppearance(userInput, userId)
        if cur_section == "GetPlayerStrength":
            print("Calling getPlayerStrength")
            return doGetPlayerStrength(userInput, userId)
        if cur_section == "GetPlayerIntelligence":
            print("Calling getPlayerIntelligence")
            return doGetPlayerIntelligence(userInput, userId)
        if cur_section == "GetPlayerDexterity":
            return doGetPlayerDexterity(userInput, userId)
        if cur_section == "GetPlayerCharisma":
            return doGetPlayerCharisma(userInput, userId)
        if cur_section == "GetPlayerWisdom":
            return doGetPlayerWisdom(userInput, userId)
        if cur_section == "GetPlayerConstitution":
            return doGetPlayerConstitution(userInput, userId)
        if cur_section == "ConfirmPlayerStats":
            print("Calling confirmPlayerStats")
            return doConfirmPlayerStats(userInput, userId)
        if cur_section == "MainGameLoop":
            return do_main_loop(userInput, userId)
        if cur_section == "Restart":
            all_global_vars._userIdList.pop(userId)
            return doSectionStarting(userId)

        # Avoid infinite loop if an unknown section is set
        return f"Error: Unknown game section '{cur_section}'. Try 'restart'.<BR>"
        

def main():
    userInput = ""
    while True:
        print(getOutput(userInput, userId = 1))
        userInput = getInput()

if __name__ == "__main__":
    main()
    