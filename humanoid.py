# Defines Player Character class, currently only stores the player's name #
from all_global_vars import all_global_vars
from open_ai_api import call_ai
from pymongo import MongoClient
from dotenv import load_dotenv
from datetime import datetime
from room import room_holder
import os
import uuid
import random


load_dotenv()
client = MongoClient(os.getenv('URI'))
db = client["dungeons_droids"]
char_collection = db["characters"]
npc_collection = db["npcs"]


class Humanoid:
    """
    Parent humanoid class. Default class to generate Player Characters as well as NPCs. Stores shared functions
    between both classes.
    """
    def __init__(self):
        self._name = None
        self._race = None
        self._class = None
        self._level = 1
        self._health = 100
        self._mana = 60
        self._str = None
        self._int = None
        self._dex = None
        self._inventory = []

    def get_name(self):
        return self._name

    def get_health(self):
        return self._health

    def get_mana(self):
        return self._mana

    def get_inventory(self):
        return list(self._inventory)

    def set_name(self, name_to_set):
        self._name = name_to_set

    def set_str(self, new_str_count):
        self._str = new_str_count

    def add_item(self, item_obj):
        if not item_obj:
            return
        self._inventory.append(item_obj)

    def remove_item(self, item_name):
        if not item_name:
            return None
        for idx, val in enumerate(self._inventory):
            if isinstance(val, dict) and val.get("name", "").lower() == item_name.lower():
                return self._inventory.pop(idx)
            if isinstance(val, str) and val.lower() == item_name.lower():
                return self._inventory.pop(idx)
        return None

    def level_up(self):
        self._level += 1


class PlayerCharacter(Humanoid):
    def __init__(self):
        super().__init__()
        self._exp = 0
        self._section = "Starting"
        self._theme = None
        self._rooms = room_holder()
        self._world_map = []

    # def get_player_character_id(self):
    #     return self._player_character_id

    def get_char_by_id(self, charId):
        """
        Retrieves a user doc via user_id.
        """
        user_doc = char_collection.find_one({"_id": charId})
        return user_doc

    def get_current_exp(self):
        return self._exp

    def get_section(self):
        return self._section

    def get_theme(self):
        return self._theme

    def get_room_array(self):
        return self._rooms

    def get_room_id_at(self, x, y):
        for e in self._world_map:
            if e["x"] == x and e["y"] == y:
                return e["room_id"]
        return None

    def get_world_map(self):
        return self._world_map

    def set_exp(self, new_exp_count):
        self._exp = new_exp_count

    def set_section(self, section):
        self._section = section

    def set_theme(self, theme):
        self._theme = theme

    def update_player_id(self, new_id):
        self.player_id = new_id

    def update_player_class(self, new_class):
        self._class = new_class

    def update_world_map(self, room_id, x, y):
        for entry in self._world_map:
            if entry["x"] == x and entry["y"] == y:
                entry["room_id"] = room_id
                return
        self._world_map.append({"x": x, "y": y, "room_id": room_id})

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
            "theme": self._theme,
            "rooms_visited": self._rooms.to_dict(),
            "world_map": self._world_map,
            "inventory": list(self._inventory),
        }

        result = char_collection.insert_one(char_doc)
        print(f"Character stored with character_id: {result.inserted_id}")
        return result.inserted_id

    def update_player_character(self, charId):
        """
        Update any new information about the player character to the DB
        """
        if not charId:
            raise ValueError("Unable to update, no character ID set")

        update_doc = {
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
            "theme": self._theme,
            "rooms_visited": self._rooms.to_dict(),
            "world_map": self._world_map,
            "inventory": list(self._inventory),
        }

        result = char_collection.update_one({"_id": charId}, {"$set": update_doc})

        print(f"Character {charId} update result: {result.modified_count} modified")
        return result

    @classmethod
    def rehydrate_char(cls, character_id):
        """
        Collect data from DB to reinitialize the character object for the session
        """
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
        returning_character._section = character_doc.get("section")
        returning_character._theme = character_doc.get("theme")
        returning_character._inventory = character_doc.get("inventory", []) or []
        returning_character._world_map = character_doc.get("world_map", []) or []

        rooms_doc = character_doc.get("rooms_visited")
        returning_character._rooms = returning_character._rooms.from_dict(rooms_doc) if rooms_doc else room_holder()

        return returning_character

    def update_char(self, userId, updates):
        """
        Updates a user doc with the given updates.
        """
        query_filter = {"_id": userId}
        update_operation = {"$set": updates}

        result = char_collection.update_one(query_filter, update_operation)
        print(f"User {userId} update result: {result.modified_count} modified")
        return result

    @classmethod
    def delete_character(self, charId):
        """
        Deletes a user from the database.
        """
        result = char_collection.delete_one({"_id": charId})
        print(f"Character {charId} delete result: {result.deleted_count} deleted")
        return result


class Npc(Humanoid):
    def __init__(self, userId):
        super().__init__()
        self._room_x = None
        self._room_y = None
        self._toughness = random.randint(1, 100)
        self._friendlyness = random.randint(1, 100)
        self._name = call_ai("Pick a name for A NPC with the theme " +
                             all_global_vars.get_player_character(userId).get_theme() +
                             " that has a toughness of " + str(self._toughness) +
                             " out of 100, with 100/100 being very tough" +
                             " and has a friendliness score where 100 is very friendly and 0 is very hostile of " +
                             str(self._friendlyness) +
                             " Just include the name by itself, don't put any other words in the response")

        self._description = call_ai("Describe the NPC with the name " + self._name + "and the theme " +
                                    all_global_vars.get_player_character(userId).get_theme() +
                                    " that has a toughness of " + str(self._toughness) +
                                    " out of 100, with 100/100 being very tough" +
                                    " and has a friendliness score where 100 is very friendly and 0 is very" +
                                    " hostile of " + str(self._friendlyness) +
                                    " Just write about a paragraph of plain text to describe the npc, like in a novel")

        self._past_conversation = []

    def set_room(self, x_pos, y_pos):
        self._room_x = x_pos
        self._room_y = y_pos

    def get_npc_by_id(self, npc_id):
        """
        Retrieves a user doc via user_id.
        """
        user_doc = npc_collection.find_one({"_id": npc_id})

        # If no npc has been generated yet
        if user_doc is None:
            return None

        return user_doc

    def get_room(self):
        return self._room_x, self._room_y

    def get_toughness(self):
        return self._toughness

    def get_friendlyness(self):
        return self._friendlyness

    def get_name(self):
        return self._name

    def get_description(self):
        return self._description

    def get_past_convo(self):
        return self._past_conversation

    def talk(self, userId, talk_string):
        call_string = "For the NPC named " + self._name + " with the descrption " + self._description
        call_string += " with the conversation history: "
        for line in (self._past_conversation or []):
            call_string += line + " "
        call_string += "And the current thing they're saying is: " + talk_string
        call_string += "Say just the response text you'd say in a conversation as that npc, nothing else"
        response = call_ai(call_string)
        self._past_conversation.append(talk_string)
        self._past_conversation.append(response)
        self.update_npc(self._id, {"conversations": self._past_conversation})
        return self._name + " says " + response

    def allow_pass(self, userId):
        print("In allow pass")
        call_string = "Based on the conversation: "
        for line in self._past_conversation:
            call_string += line + " "
        call_string += f"And the player wants to go past the npc with friendlynes {self._friendlyness} out of 100"
        call_string += (" Do you allow the player to pass? Don't let them pass unless they've had a good" +
                        " conversation with you, or if you've said they could pass it's okay. Don't be too" +
                        " difficult to get past, be simple. Answer with one word, yes or no")
        print("Calling AI")
        response = call_ai(call_string)
        print("Got response: " + str(response))
        if response.strip().lower().startswith("no"):
            self._past_conversation.append(
                "Note: The player tried to go past the npc to exit the room here and was blocked")
            return False
        self._past_conversation.append(
            "Note: The player tried to go past the npc to exit the room here and was allowed")
        return True

    def store_npc(self):
        """
        Stores a player_character object in the MongoDB and returns the player_character_id.
        """
        # Convert npc object to dictionary
        npc_doc = {
            "name": self.get_name(),
            "description": self.get_description(),
            "race": self._race,
            "class": self._class,
            "level": self._level,
            "health": self.get_health(),
            "mana": self.get_mana(),
            "str": self._str,
            "int": self._int,
            "dex": self._dex,
            "inventory": list(self._inventory),
            "x_pos": self._room_x,
            "y_pos": self._room_y,
            "toughness": self._toughness,
            "friendlyness": self._friendlyness,
            "conversations": self._past_conversation,
            "created_at": datetime.now(),
        }

        result = npc_collection.insert_one(npc_doc)
        self._id = result.inserted_id
        print(f"NPC stored with npc_id: {result.inserted_id}")
        return result.inserted_id

    @classmethod
    def rehydrate_npc(cls, npc_id):
        """
        Collect data from DB to reinitialize the character object for the session
        """
        npc = cls.__new__(cls)  # Create a returning character object
        Humanoid.__init__(npc)

        character_doc = npc.get_npc_by_id(npc_id)  # Get existing details of saved character
        if character_doc is None:
            return None

        # Begin loading saved details
        npc._id = character_doc.get("_id")
        npc._name = character_doc.get("name") or "Unknown"
        npc._description = character_doc.get("description") or ""
        npc._race = character_doc.get("race")
        npc._class = character_doc.get("class")
        npc._level = character_doc.get("level", 1)
        npc._health = character_doc.get("health", 100)
        npc._mana = character_doc.get("mana", 60)
        npc._str = character_doc.get("str")
        npc._int = character_doc.get("int")
        npc._dex = character_doc.get("dex")
        npc._inventory = character_doc.get("inventory", []) or []
        npc._room_x = character_doc.get("x_pos")
        npc._room_y = character_doc.get("y_pos")
        npc._toughness = character_doc.get("toughness")
        npc._friendlyness = character_doc.get("friendlyness")
        npc._past_conversation = character_doc.get("conversations") or []
        return npc

    def update_npc(self, npc_id, updates):
        """
        Updates an NPC doc by npc_id with the given updates (dict of field: value).
        """
        query_filter = {"_id": npc_id}
        update_operation = {"$set": updates}

        result = npc_collection.update_one(query_filter, update_operation)
        print(f"NPC {npc_id} update result: {result.modified_count} modified")
        return result