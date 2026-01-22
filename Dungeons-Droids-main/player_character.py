# Defines Player Character class, currently only stores the player's name #
import uuid


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
        self._player_character_id = str(uuid.uuid4())
        self._inventory = []  # List to store Item objects

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

    def set_exp(self, new_exp_count):
        self._exp = new_exp_count

    def set_name(self, name_to_set):
        self._name = name_to_set

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
    
    def add_item(self, item):
        """Add an item to the player's inventory"""
        self._inventory.append(item)
    
    def remove_item(self, item_name):
        """Remove an item from inventory by name"""
        for item in self._inventory:
            if item.get_name().lower() == item_name.lower():
                self._inventory.remove(item)
                return item
        return None
    
    def get_inventory(self):
        """Get the player's inventory"""
        return self._inventory
    
    def has_item(self, item_name):
        """Check if player has an item"""
        for item in self._inventory:
            if item.get_name().lower() == item_name.lower():
                return True
        return False
