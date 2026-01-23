# Defines Player Character class, currently only stores the player's name #
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from room import room_holder
import os
import uuid

load_dotenv()
client = MongoClient(os.getenv('URI'))
db = client["dungeons_droids"]
collection = db["characters"]

class player_character:
    def __init__(self):
        self._name = None
        self._race = None
        self._class = None
        self._level = 1
        self._exp = 0
        self._health = 100
        self._mana = 60
        self._str = None
        self._int = None
        self._dex = None
        self._section = "Starting"
        self._rooms = room_holder()

    def get_player_character_id(self):
        return self._player_character_id

    def get_health(self):
        return self._health

    def get_mana(self):
        return self._mana

    def get_name(self):
        return self._name

    def get_current_exp(self):
        return self._exp

    def get_room_array(self):
        return self._rooms

    def get_section(self):
        return self._section

    def set_exp(self, new_exp_count):
        self._exp = new_exp_count

    def set_str(self, new_str_count):
        self._str = new_str_count

    def set_name(self, name_to_set):
        self._name = name_to_set

    def set_section(self, section):
        self._section = section

    def level_up(self):
        self._level += 1

    def update_player_id(self, new_id):
        self.player_id = new_id

    def update_player_class(self, new_class):
        self._class = new_class

    def earned_exp(self, new_exp):
        current_exp = self.get_current_exp()
        current_exp += new_exp
        if current_exp >= 100:
            current_exp = current_exp - 100
            self.set_exp(current_exp)
            self.level_up()

    def store_player_character(self):
        """
        Stores a player_character object in the MongoDB and returns the player_character_id.
        """
        # Convert player_character object to dictionary
        char_doc = {
            "name": self.get_name(),
            "race": self._race,
            "class": self._class,
            "level": self._level,
            "exp": self.get_current_exp(),
            "health": self.get_health(),
            "mana": self.get_mana(),
            "str": self._str,
            "int": self._int,
            "dex": self._dex,
            "created_at": datetime.now(),
            "section": self._section,
            "rooms_visited": self._rooms.to_dict()
        }

        result = collection.insert_one(char_doc)
        print(f"Character stored with character_id: {result.inserted_id}")
        return result.inserted_id

    def get_char_by_id(self, charId):
        """
        Retrieves a user doc via user_id.
        """
        user_doc = collection.find_one({"_id": charId})
        return user_doc

    @classmethod
    def rehydrate_char(cls, character_id):
        returning_character = cls()    # Create a returning character object
        character_doc = returning_character.get_char_by_id(character_id)    # Get existing details of saved character

        # Begin loading saved details
        returning_character._player_character_id = character_doc.get("_id")
        returning_character._name = character_doc.get("name")
        returning_character._race = character_doc.get("race")
        returning_character._class = character_doc.get("class")
        returning_character._level = character_doc.get("level", 1)
        returning_character._exp = character_doc.get("exp", 0)
        returning_character._health = character_doc.get("health", 100)
        returning_character._mana = character_doc.get("mana", 60)
        returning_character._str = character_doc.get("str")
        returning_character._int = character_doc.get("int")
        returning_character._dex = character_doc.get("dex")
        returning_character._section = character_doc.get("section", "Starting")

        rooms_doc = character_doc.get("rooms_visited")
        returning_character._rooms = returning_character._rooms.from_dict(rooms_doc) if rooms_doc else room_holder()

        return returning_character

    def update_char(self, charId, updates):
        """
        Updates a user doc with the given updates.
        """
        query_filter = {"_id": charId}
        update_operation = {"$set": updates}

        result = collection.update_one(query_filter, update_operation)
        print(f"Character {charId} update result: {result.modified_count} modified")
        return result

    def delete_user(self, charId):
        """
        Deletes a user from the database.
        """
        result = collection.delete_one({"_id": charId})
        print(f"Character {charId} delete result: {result.deleted_count} deleted")
        return result
