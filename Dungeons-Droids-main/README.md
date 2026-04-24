Dungeons & Droids: AI Powered Text-Adventure Game

Dungeons & Droids is a single player focused MUD style game, with generative AI features. The 
game will dynamically generate rooms, NPCs, items and conversations using a LLM API while also
allowing players to retain their characters via sessions storage with MongoDB. 

In the game, players will explore a grid-based dungeon, interacting with AI-driven NPCs while 
managing their inventory, fighting, leveling up and more all through a web-based client. 

## Features

- AI-generated room descriptions and NPC dialogue
- Player character retention via MongoDB
- Inventory system with items of varying rarity
- Visual room maps rendered in the web client via Pillow.

## Tech Stack

- Backend: Python, Flask
- AI-API: Google Gemini (Can use OpenAI, but Gemini response times are exceptionally faster)
- Database: MongoDB
- Image/Map Generation: Pillow
- Authentication: bcrypt
- Frontend: HTML

## Setup & Installation

### Prerequisites
- Python 3.10+
- MongoDB (local or cloud)
- Google Gemini API key

### Installation
1. Clone the repository
2. Create and activate a virtual environment:
    - In bash: 
        - python -m venv .venv
        - source .venv/bin/activate
3. Install dependencies:
    - In bash:
        - pip install -r requirements.txt
4. Create a .env file
    - Place your keys in the file like so:
        - URI=<your MongoDB connection string>
        - OPENAI_API_KEY=<your API key>
5. Run the program:
    - In bash:
        - python app.py
6. Open your browser and navigate to 127.0.0.1:5000

## How to play
After navigating to the proper address, you will be greeted with an authentication page. 
If you have created an account before, login using your previously created usernam and password.
If you have not created an account, simply enter in your desired username and password and click
'create account.' 

Upon first login, you will be created with the character creator. Respond to the prompts to create
your desired character.

After character creation is completed, you wil be presented with a world and your character will
begin their journey in their first room! Below are some commands to keep in mind while playing.

### Commands
- 'north', 'south', 'east', 'west' --> Navigate to the room in the respective direction
- 'look' --> Describe the current room you find yourself in
- 'describe npc' --> Describe the npc inhabiting the room your currently occupy
- 'say <message>' --> Talk to the npc
- 'inventory' --> View your inventory
- 'pickup <item>' --> Pickup an item in the room your currently occupy
- 'drop <item>' --> Drop an item from your inventory onto the floor of the room. 
- 'restart' --> Restart the game and enter character creation again.
- 'help' --> Show the commands available to you.

## File Overview
- 'app.py' --> Entry point for Flask handling, API requests and sessions
- 'hello.py' --> Core game state logic
- 'main_loop.py' --> Command parsing and gameplay main_loop
- 'player_character.py' --> Player character class and save/load persistence 
- 'room.py' --> Dungeon grid layout and room generation w/ minimap rendering and navigation
- 'npc.py' --> NPC class with AI generation and conversation handling
- 'map_generator.py' --> Pillow utilization in room map generation
- 'all_global_vars.py' --> Current session state container

## Future Features
- Combat system
- Quests and Experience
- Expanded dungeon generation
- Skill/Spell acquisition
