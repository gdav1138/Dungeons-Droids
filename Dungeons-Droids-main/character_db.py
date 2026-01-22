from pymongo import MongoClient
from dotenv import load_dotenv
from player_character import player_character
from datetime import datetime
import os



load_dotenv()
client = MongoClient(os.getenv('URI'))
db = client["dungeons_droids"]
collection = db["characters"]


def store_player_character(player_character_obj):
    """
    Stores a player_character object in the MongoDB and returns the player_character_id.
    """
    # Convert player_character object to dictionary
    char_doc = {
        "name": player_character_obj.get_name(),
        "race": player_character_obj._race,
        "class": player_character_obj._class,
        "level": player_character_obj._level,
        "exp": player_character_obj.get_current_exp(),
        "health": player_character_obj.get_health(),
        "mana": player_character_obj.get_mana(),
        "str": player_character_obj._str,
        "int": player_character_obj._int,
        "dex": player_character_obj._dex,
        "created_at": datetime.now(),
    }
    
    result = collection.insert_one(char_doc)
    print(f"Character stored with character_id: {result.inserted_id}")
    return result.inserted_id


def get_char_by_id(char_id):
    """
    Retrieves a user doc via user_id.
    """
    user_doc = collection.find_one({"_id": char_id})
    return user_doc


def update_char(char_id, updates):
    """
    Updates a user doc with the given updates.
    """
    query_filter = {"_id": char_id}
    update_operation = {"$set": updates}

    result = collection.update_one(query_filter, update_operation)
    print(f"Character {char_id} update result: {result.modified_count} modified")
    return result


def delete_user(char_id):
    """
    Deletes a user from the database.
    """
    result = collection.delete_one({"_id": char_id})
    print(f"Character {char_id} delete result: {result.deleted_count} deleted")
    return result


def query_doc(dict_param):
    """
    Query function to pull character if needed.
    """
    results = collection.find_one(dict_param)
    return results
