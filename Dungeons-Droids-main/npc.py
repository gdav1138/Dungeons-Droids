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
            str(self._friendlyness) + " Just include the name by itself, don't put any other words in the response")
            
        self._description = call_ai("Describe the NPC with the name " + self._name + "and the theme " + 
            all_global_vars.get_theme(userId)._era +
            " that has a toughness of " + str(self._toughness) + " out of 100, with 100/100 being very tough" + 
            " and has a friendliness score where 100 is very friendly and 0 is very hostile of " + 
            str(self._friendlyness) + " Just write about a paragraph of plain text to describe the npc, like in a novel")

        self._past_conversation = []
    
    def talk(self, userId, talk_string):
        call_string = "For the NPC named " + self._name + " with the descrption " + self._description
        call_string += " with the conversation history: "
        for line in self._past_conversation:
            call_string += line + " " 
        call_string += "And the current thing they're saying is: "  + talk_string
        call_string += "Say just the response text you'd say in a conversation as that npc, nothing else"
        response =  call_ai(call_string)
        self._past_conversation.append(talk_string)
        self._past_conversation.append(response)
        return self._name + " says " + response

