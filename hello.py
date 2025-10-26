#print("Hello World")
from openai import OpenAI
from dotenv import load_dotenv
from all_global_vars import all_global_vars
import os


def doSectionStarting(userId):
    print("Starting up with userID: " + userId)
    

    client_response = ""
    response = client.responses.create(
        model="gpt-5-nano",
        input="Greet the player as our new Text Game With AI Called Dungeons and Droids. Don't give any instructions to the user. Make it about 2 sentences."
    )
    client_response += response.output_text + "\n"
    response = client.responses.create(
        model="gpt-5-nano",
        input="Pick an era for this game to take place in. Make the answer very short, just a word or two, like medieval or sci-fi"
    )

    all_global_vars.get_theme(userId)._era = response.output_text

    #print("This game takes place in the " + all_global_vars._theme._era + " era.")
    client_response += "This game takes place in the " + all_global_vars.get_theme(userId)._era + " era.\n"
    #print ("What should we call your character?")
    client_response += "What should we call your character?"
    all_global_vars.set_section(userId=userId, section="GetPlayerName")
    return client_response

def doGetPlayerName(userInput, userId):
    client_response = ""
    new_name = userInput
    all_global_vars.get_player_character(userId).set_name(new_name)

    setup_string = "Make up a location or MUD room description fitting the theme " + all_global_vars.get_theme(userId)._era + " for a character named " + all_global_vars.get_player_character(userId).get_name() + ". Don't list any exits or items or anything other than a description of a location."

    print("Calling gpt in getplayername")
    response = client.responses.create(
        model="gpt-5-nano",
        input=setup_string
    )
    client_response += response.output_text + "\n"
    all_global_vars.set_section(userId, "Finished")
    print("Returning client-response")
    return client_response

def getInput():
    return input()

def getOutput(userInput, userId):
    
    if userId not in all_global_vars._userIdList:
        print("UserID not in userIdList")
        all_global_vars.create_player(userId)
    cur_section = all_global_vars.get_section(userId)
    if cur_section == "Starting":
        print("Calling doStarting")
        return doSectionStarting(userId)
    if cur_section == "GetPlayerName":
        print("Calling getplayerName")
        return doGetPlayerName(userInput, userId)
    if cur_section == "Finished":
        return "Game Over!"


load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def main():
    userInput = ""
    while True:
        print(getOutput(userInput, userId = 1))
        userInput = getInput()

if __name__ == "__main__":
    main()