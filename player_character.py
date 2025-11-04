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
