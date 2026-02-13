from open_ai_api import call_ai
from all_global_vars import all_global_vars
from quests import create_random_quest
import random

class npc:
    def _player_profile(self, userId):
        """Build a short player profile string for prompting NPC behavior."""
        pc = all_global_vars.get_player_character(userId)
        name = getattr(pc, "_name", None) or "the player"

        # Stats (missing -> 0)
        try:
            stats = pc.get_stats()
        except Exception:
            stats = {
                "str": getattr(pc, "_str", 0) or 0,
                "int": getattr(pc, "_int", 0) or 0,
                "dex": getattr(pc, "_dex", 0) or 0,
                "cha": getattr(pc, "_cha", 0) or 0,
                "wis": getattr(pc, "_wis", 0) or 0,
                "con": getattr(pc, "_con", 0) or 0,
            }

        # Appearance
        try:
            app = pc.get_appearance()
        except Exception:
            app = {}
        pronouns = (app.get("pronouns") or "").strip()
        summary = (app.get("summary") or "").strip()

        parts = [f"Player name: {name}."]
        if pronouns:
            parts.append(f"Player pronouns: {pronouns}.")
        if summary:
            parts.append(f"Player appearance: {summary}.")
        parts.append(
            "Player stats (0-10): "
            f"STR {stats.get('str', 0)}, INT {stats.get('int', 0)}, DEX {stats.get('dex', 0)}, "
            f"CHA {stats.get('cha', 0)}, WIS {stats.get('wis', 0)}, CON {stats.get('con', 0)}."
        )
        return " ".join(parts)

    def _interaction_modifiers(self, userId):
        """Compute simple, explainable modifiers for negotiation."""
        pc = all_global_vars.get_player_character(userId)
        try:
            s = pc.get_stats()
        except Exception:
            s = {}
        str_ = int(s.get("str", getattr(pc, "_str", 0) or 0) or 0)
        int_ = int(s.get("int", getattr(pc, "_int", 0) or 0) or 0)
        dex_ = int(s.get("dex", getattr(pc, "_dex", 0) or 0) or 0)
        cha_ = int(s.get("cha", getattr(pc, "_cha", 0) or 0) or 0)
        wis_ = int(s.get("wis", getattr(pc, "_wis", 0) or 0) or 0)
        con_ = int(s.get("con", getattr(pc, "_con", 0) or 0) or 0)

        # Persuasion: CHA primary, INT/WIS help wording/reading the room
        persuasion = cha_ + (int_ // 3) + (wis_ // 3)
        # Intimidation: STR primary, CON backing
        intimidation = str_ + (con_ // 2)
        # Awareness: WIS primary, INT secondary (used for NPC reading the player)
        awareness = wis_ + (int_ // 2)
        # Agility/escape: DEX
        agility = dex_
        return {
            "persuasion": persuasion,     # ~0-16
            "intimidation": intimidation, # ~0-15
            "awareness": awareness,       # ~0-15
            "agility": agility,           # 0-10
        }

    def __init__(self, userId):
        self._toughness = random.randint(1,100)
        self._friendlyness = random.randint(1,100)
        self._name = call_ai("Pick a name for A NPC with the theme " + 
            all_global_vars.get_player_character(userId).get_theme() +
            " that has a toughness of " + str(self._toughness) + " out of 100, with 100/100 being very tough" + 
            " and has a friendliness score where 100 is very friendly and 0 is very hostile of " + 
            str(self._friendlyness) + " Just include the name by itself, don't put any other words in the response")
            
        self._description = call_ai("Describe the NPC with the name " + self._name + "and the theme " + 
            all_global_vars.get_player_character(userId).get_theme() +
            " that has a toughness of " + str(self._toughness) + " out of 100, with 100/100 being very tough" + 
            " and has a friendliness score where 100 is very friendly and 0 is very hostile of " + 
            str(self._friendlyness) + " Just write about a paragraph of plain text to describe the npc, like in a novel")

        self._past_conversation = []
        # Chance that this NPC has a quest to offer (defeat enemies, obtain item, obtain gold, etc.)
        theme = all_global_vars.get_player_character(userId).get_theme() or "fantasy"
        self._quest_to_offer = create_random_quest(theme, self._name) if random.random() < 0.35 else None
    
    def talk(self, userId, talk_string):
        mods = self._interaction_modifiers(userId)
        call_string = "For the NPC named " + self._name + " with the descrption " + self._description
        call_string += " " + self._player_profile(userId) + " "
        call_string += ("When responding, subtly factor in the player's stats and appearance. "
                        "High CHA should make the NPC more receptive to polite persuasion. "
                        "High STR/CON should make intimidation more effective (even if unspoken). "
                        "High WIS/INT should help the player come across as perceptive/credible. "
                        "High DEX might make the NPC wary of sudden moves. "
                        f"Negotiation modifiers: persuasion {mods['persuasion']}/16, "
                        f"intimidation {mods['intimidation']}/15, awareness {mods['awareness']}/15.")
        call_string += " with the conversation history: "
        for line in self._past_conversation:
            call_string += line + " " 
        call_string += "And the current thing they're saying is: "  + talk_string
        call_string += "Say just the response text you'd say in a conversation as that npc, nothing else"
        response = call_ai(call_string)
        self._past_conversation.append(talk_string)
        self._past_conversation.append(response)

        out = self._name + " says " + response

        # Sometimes offer a quest if this NPC has one and the player doesn't have it yet
        if self._quest_to_offer:
            pc = all_global_vars.get_player_character(userId)
            if not pc.has_quest(self._quest_to_offer["id"]) and random.random() < 0.4:
                pc.add_quest(self._quest_to_offer)
                q = self._quest_to_offer
                out += (
                    f" Then {self._name} adds: I have a task for you, if you're willing. "
                    f"{q['description']} In return, I can offer {q['reward_description']}. "
                    "(Quest added to your log. Type 'quests' to view.)"
                )
                self._quest_to_offer = None

        return out

    def allow_pass(self, userId):
        print("In allow pass")
        mods = self._interaction_modifiers(userId)
        call_string = "Based on the conversation: " 
        for line in self._past_conversation:
            call_string += line + " " 
        call_string += " " + self._player_profile(userId) + " "
        call_string += (f"And the player wants to go past the npc with friendliness {self._friendlyness} out of 100. "
                        "Decide if you allow the player to pass. "
                        "Use the conversation plus the player's stats/appearance. "
                        "If persuasion modifier is high (>=10), be easier to convince. "
                        "If intimidation modifier is high (>=10) and the player was threatening, be more likely to allow pass. "
                        "If awareness is high, the player may have noticed something to say that convinces you. "
                        "Don't let them pass unless they've had a good conversation with you, or if you've said they could pass it's okay. "
                        "Don't be too difficult to get past, be simple. "
                        f"Modifiers: persuasion {mods['persuasion']}/16, intimidation {mods['intimidation']}/15, awareness {mods['awareness']}/15. "
                        "Answer with one word, yes or no.")
        print("Calling AI")
        response = call_ai(call_string)
        print("Got response: " + str(response))
        if  response.strip().lower().startswith("no"): 
            self._past_conversation.append("Note: The player tried to go past the npc to exit the room here and was blocked")
            return False
        self._past_conversation.append("Note: The player tried to go past the npc to exit the room here and was allowed")
        return True