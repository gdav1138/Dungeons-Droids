Dungeons and Droids: AI Powered Text-Adventure Game

Current Setup Instructions:
pip install -r requirements.txt

Create a new file named '.env', and inside the file add: OPENAI_API_KEY = 'YOUR OPENAI_API KEY'
Replace 'YOUR OPENAI_API KEY' with your specific OpenAI Key (without the '')

Current Structure:
app.py - Flask implementation
hello.py - Currently used to test our OpenAI API
gameloop.html - Web page user interface
all_global_vars.py - Global state tracking
player_character.py - Store player information
theme.py - Sets the current theme of the dungeon
