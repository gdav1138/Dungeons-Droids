from open_ai_api import call_ai
from all_global_vars import all_global_vars
import random

class npc:
    def __init__(self, userId):
        self._toughness = random.randint(1,100)
        self._friendlyness = random.randint(1,100)
        self._name = call_ai("Pick a name for A NPC with the theme " + 
            all_global_vars.get_theme(userId)._era + 
            " that has a toughness of " + str(self._toughness) + " out of 100, with 100/100 being very tough" + 
            " and has a friendliness score where 100 is very friendly and 0 is very hostile of " + 
            str(self._friendlyness) )
            
        self._description = call_ai("Describe the NPC with the name " + self._name + "and the theme " + 
            all_global_vars.get_theme(userId)._era +
            " that has a toughness of " + str(self._toughness) + " out of 100, with 100/100 being very tough" + 
            " and has a friendliness score where 100 is very friendly and 0 is very hostile of " + 
            str(self._friendlyness) )
        