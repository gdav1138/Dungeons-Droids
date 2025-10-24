#print("Hello World")
from openai import OpenAI
from dotenv import load_dotenv
from all_global_vars import all_global_vars
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

response = client.responses.create(
    model="gpt-5-nano",
    input="Greet the player as our new Text Game With AI Called Dungeons and Droids. Don't give any instructions to the user. Make it about 2 sentences."
)
print(response.output_text)

response = client.responses.create(
    model="gpt-5-nano",
    input="Pick an era for this game to take place in. Make the answer very short, just a word or two, like medieval or sci-fi"
)

all_global_vars._theme._era = response.output_text

print("This game takes place in the " + all_global_vars._theme._era + " era.")

#may need to revise for the web
print ("What should we call your character?")
new_name = input()
all_global_vars._player_character.set_name(new_name)

setup_string = "Make up a location or MUD room description fitting the theme " + all_global_vars._theme._era + " for a character named " + all_global_vars._player_character.get_name() + ". Don't list any exits or items or anything other than a description of a location."

response = client.responses.create(
    model="gpt-5-nano",
    input=setup_string
)
print(response.output_text)
