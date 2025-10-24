from player_character import player_character
from theme import theme

class all_global_vars_class:
    def __init__(self):
        self._player_character = player_character()
        self._theme = theme()


all_global_vars = all_global_vars_class()