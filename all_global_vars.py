from player_character import player_character
from theme import theme

class all_global_vars_class:
    def __init__(self):
        self._userIdList = dict()
    
    def create_player(self, userId):
        self._userIdList[userId] = dict()
        self._userIdList[userId]["player_character"] = player_character()
        self._userIdList[userId]["theme"] = theme()
        self._userIdList[userId]["section"] = "Starting"

    def get_player_character(self, userId):
        return self._userIdList[userId]["player_character"]
    
    def get_theme(self, userId):
        return self._userIdList[userId]["theme"]
    
    def get_section(self, userId):
        return self._userIdList[userId]["section"]
    def set_section(self, userId, section):
        self._userIdList[userId]["section"] = section

all_global_vars = all_global_vars_class()