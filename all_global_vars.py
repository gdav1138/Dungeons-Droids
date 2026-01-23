# Stores all global variables, per user-game based on their userID                       
# This is a key part of the program, and this will be stored in a database ASAP.
# Each players variables have to be saved between commands so the web server can
# remember them across commands and sessions.

from theme import theme


class all_global_vars_class:
    """Global container for all user sessions"""

    def __init__(self):
        self._userIdList = dict()

    def create_player(self, userId):
        """Creates new player entry"""
        self._userIdList[userId] = dict()
        self._userIdList[userId]["player_character"] = None
        self._userIdList[userId]["theme"] = theme()
        self._userIdList[userId]["section"] = "Starting"
        
        #has to be here to avoid circular imports
        from room import room_holder
        self._userIdList[userId]["rooms"] = room_holder()

        # has to be here to avoid circular imports
        from room import room_holder
        self._userIdList[userId]["rooms"] = room_holder()

    def get_player_character(self, userId):
        return self._userIdList[userId]["player_character"]

    def get_theme(self, userId):
        return self._userIdList[userId]["theme"]

    def get_section(self, userId):
        return self._userIdList[userId]["section"]

    def set_player_character(self, userId, player_character):
        self._userIdList[userId]["player_character"] = player_character

    def set_theme(self, userId, theme):
        self._userIdList[userId]["theme"] = theme

    def set_section(self, userId, section):
        self._userIdList[userId]["section"] = section
    
    def get_room_holder(self, userId):
        return self._userIdList[userId]["rooms"]

    def get_room_holder(self, userId):
        return self._userIdList[userId]["rooms"]

    def rehydrate_globals(self, userId, user_doc, returning_character):
        self.set_player_character(userId, returning_character)
        self.set_theme(userId, user_doc.get("theme"))
        self.set_section(userId, returning_character.get_section())


all_global_vars = all_global_vars_class()