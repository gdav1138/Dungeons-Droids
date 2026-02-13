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
        # Expanded stats (used for NPC interactions and future checks)
        self._cha = None  # charisma
        self._wis = None  # wisdom
        self._con = None  # constitution
        self._section = "Starting"
        self._theme = None
        self._rooms = room_holder()
        self._inventory = []  # list of item dicts {name, rarity, value, desc}
        self._quests = []  # list of quest dicts from quests.py (id, type, target, description, etc.)
        # Appearance/customization (freeform + optional structured fields)
        self._appearance = {
            "summary": None,          # 1-sentence description
            "pronouns": None,         
            "hair": None,
            "eyes": None,
            "outfit": None,
            "feature": None,          # distinguishing feature
        }

    def get_player_character_id(self):
        return self._player_character_id

    def get_health(self):
        return self._health

    def get_mana(self):
        return self._mana

    def get_name(self):
        return self._name

    def get_appearance(self):
        return dict(self._appearance) if isinstance(self._appearance, dict) else {}

    def get_stats(self):
        """Return a normalized dict of core stats (missing -> 0)."""
        def n(v):
            try:
                return int(v)
            except Exception:
                return 0
        return {
            "str": n(self._str),
            "int": n(self._int),
            "dex": n(self._dex),
            "cha": n(self._cha),
            "wis": n(self._wis),
            "con": n(self._con),
        }

    def get_current_exp(self):
        return self._exp

    def get_room_array(self):
        return self._rooms

    def get_inventory(self):
        return list(self._inventory)

    def get_quests(self):
        return list(self._quests)

    def add_quest(self, quest_dict):
        if not quest_dict or not isinstance(quest_dict, dict):
            return
        if self.has_quest(quest_dict.get("id")):
            return
        self._quests.append(dict(quest_dict))

    def has_quest(self, quest_id):
        if not quest_id:
            return False
        return any(
            (q.get("id") == quest_id for q in self._quests)
        )

    def get_section(self):
        return self._section

    def get_theme(self):
        return self._theme

    def set_exp(self, new_exp_count):
        self._exp = new_exp_count

    def set_str(self, new_str_count):
        self._str = new_str_count

    def set_int(self, new_int_count):
        self._int = new_int_count

    def set_dex(self, new_dex_count):
        self._dex = new_dex_count

    def set_cha(self, new_cha_count):
        self._cha = new_cha_count

    def set_wis(self, new_wis_count):
        self._wis = new_wis_count

    def set_con(self, new_con_count):
        self._con = new_con_count

    def set_name(self, name_to_set):
        self._name = name_to_set

    def set_appearance_summary(self, summary: str):
        if not isinstance(self._appearance, dict):
            self._appearance = {}
        self._appearance["summary"] = (summary or "").strip() or None

    def set_pronouns(self, pronouns: str):
        if not isinstance(self._appearance, dict):
            self._appearance = {}
        self._appearance["pronouns"] = (pronouns or "").strip() or None

    def set_appearance_field(self, key: str, value: str):
        if not isinstance(self._appearance, dict):
            self._appearance = {}
        if key not in ("hair", "eyes", "outfit", "feature"):
            raise ValueError("Invalid appearance key")
        self._appearance[key] = (value or "").strip() or None

    def set_section(self, section):
        self._section = section

    def set_theme(self, theme):
        self._theme = theme

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

    def update_player_id(self, new_id):
        self.player_id = new_id

    def update_player_class(self, new_class):
        self._class = new_class

    def update_rooms(self):
        self._rooms.to_

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
            "cha": self._cha,
            "wis": self._wis,
            "con": self._con,
            "appearance": dict(self._appearance) if isinstance(self._appearance, dict) else {},
            "created_at": datetime.now(),
            "section": self._section,
            "theme": self._theme,
            "rooms_visited": self._rooms.to_dict(),
            "inventory": list(self._inventory),
            "quests": list(self._quests),
        }

        result = collection.insert_one(char_doc)
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
            "cha": self._cha,
            "wis": self._wis,
            "con": self._con,
            "appearance": dict(self._appearance) if isinstance(self._appearance, dict) else {},
            "created_at": datetime.now(),
            "section": self._section,
            "theme": self._theme,
            "rooms_visited": self._rooms.to_dict(),
            "inventory": list(self._inventory),
            "quests": list(self._quests),
        }

        result = collection.update_one({"_id": charId}, {"$set": update_doc})

        print(f"Character {charId} update result: {result.modified_count} modified")
        return result

    def get_char_by_id(self, charId):
        """
        Retrieves a user doc via user_id.
        """
        user_doc = collection.find_one({"_id": charId})
        return user_doc

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
        returning_character._cha = character_doc.get("cha")
        returning_character._wis = character_doc.get("wis")
        returning_character._con = character_doc.get("con")
        returning_character._appearance = character_doc.get("appearance", {}) or {}
        returning_character._section = character_doc.get("section")
        returning_character._theme = character_doc.get("theme")
        returning_character._inventory = character_doc.get("inventory", []) or []
        returning_character._quests = character_doc.get("quests", []) or []

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

    @classmethod
    def delete_character(self, charId):
        """
        Deletes a user from the database.
        """
        result = collection.delete_one({"_id": charId})
        print(f"Character {charId} delete result: {result.deleted_count} deleted")
        return result
