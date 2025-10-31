# Main game logic file. Handles interactions between player inputs and OpenAI responses  #
# The key part of this file is the all_global_vars. That saves each players variables, associated with
# a userId. Since each web request is separate, it has to remember where in the program it is,
# which is the section portion, with get_section and set_section to say where in the program that user
# is. There's also a mainloop section that leads to another file.
from openai import OpenAI
from dotenv import load_dotenv
from all_global_vars import all_global_vars
from open_ai_api import call_ai
import os
from main_loop import do_main_loop


def doSectionStarting(userId):
    """Introduction section of the game where instructions are given to ChatGPT to greet the player, ask for their name, and set the era."""
    
    print("Starting up doSectionStarting with userID: " + str(userId))

    client_response = ""
    client_response += call_ai("Greet the player as our new Text Game With AI Called Dungeons and Droids. Don't give any instructions to the user. Make it about 2 sentences.")
    
    all_global_vars.get_theme(userId)._era = call_ai("Pick an era for this game to take place in. Make the answer very short, just a word or two, like medieval or sci-fi")

    client_response += "This game takes place in the " + all_global_vars.get_theme(userId)._era + " era.\n"
    client_response += "What should we call your character?"
    all_global_vars.set_section(userId=userId, section="GetPlayerName")
    return client_response

def doGetPlayerName(userInput, userId):
    """Handles player name input. Stores it in player_character object, and generates a themed location using OpenAI API"""
    client_response = ""
    new_name = userInput
    all_global_vars.get_player_character(userId).set_name(new_name)

    setup_string = "Make up a location or MUD room description fitting the theme " + all_global_vars.get_theme(userId)._era + " for a character named " + all_global_vars.get_player_character(userId).get_name() + ". Don't list any exits or items or anything other than a description of a location. Make it about 3 sentences."

    client_response += call_ai(setup_string) + "\n"
    all_global_vars.set_section(userId, "MainGameLoop")
    return client_response

def getInput():
    return input()

def getOutput(userInput, userId):
    
    while True:
        if userId not in all_global_vars._userIdList:
            print("UserID not in userIdList")
            all_global_vars.create_player(userId)
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
    