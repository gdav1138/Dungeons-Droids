"""
Quest system: quest types and random quest generation.

Each quest is stored as a plain dict so it can be easily serialized into MongoDB and
rehydrated back into a player character.

    {
        "id": <str uuid>,
        "type": <one of QUEST_*>,
        "target": <int|str>,    # kill count, items to collect / legacy item name, gold amount
        "description": <str>,
        "quest_giver": <str>,   # NPC name
        "reward_description": <str>,
        "reward_xp": <int>,
        "reward_gold": <int>,
        "status": "active" | "completed",
        "progress": <int>,      # generic progress counter (0+)
        "rewarded": <bool>,     # reward granted (prevents double payout)
    }

Win conditions:
- defeat_enemies: quest is complete when progress >= target (enemy kills).
- obtain_item: quest is complete when progress >= target. Target may be an int
  (collect that many items from the world) or a legacy string (one specific item name).
- obtain_gold: quest is complete when the player's gold >= target.
"""
import random
import uuid

# Quest type constants
QUEST_DEFEAT_ENEMIES = "defeat_enemies"
QUEST_OBTAIN_ITEM = "obtain_item"
QUEST_OBTAIN_GOLD = "obtain_gold"


def create_random_quest(theme: str, quest_giver_name: str) -> dict:
    """
    Create a random quest appropriate for the theme.

    Returns a quest dict with the schema documented in the module docstring.
    """
    quest_type = random.choice([
        QUEST_DEFEAT_ENEMIES,
        QUEST_OBTAIN_ITEM,
        QUEST_OBTAIN_GOLD,
    ])
    quest_id = str(uuid.uuid4())

    if quest_type == QUEST_DEFEAT_ENEMIES:
        count = 1
        description = (
            f"Defeat {count} enemy or monster. "
            f"Theme: {theme}. Return when the task is done."
        )
        target = count
        reward_xp = 12
        reward_gold = 5
        reward = f"{reward_xp} XP and {reward_gold} gold"

    elif quest_type == QUEST_OBTAIN_ITEM:
        need = random.randint(5, 10)
        description = (
            f"Pick up {need} different items from the dungeon (anything you find counts). "
            f"Theme: {theme}. They are restocking supplies."
        )
        target = need
        reward_xp = 4 * need
        reward_gold = 3 * need
        reward = f"{reward_xp} XP and {reward_gold} gold"

    else:  # QUEST_OBTAIN_GOLD
        amount = random.choice([20, 35, 50, 75])
        description = (
            f"Obtain {amount} gold (or equivalent currency) and deliver it. "
            f"Theme: {theme}. They have a debt to settle."
        )
        target = amount
        reward_xp = 15
        reward_gold = max(5, amount // 8)
        reward = f"{reward_xp} XP and {reward_gold} gold"

    return {
        "id": quest_id,
        "type": quest_type,
        "target": target,
        "description": description,
        "quest_giver": quest_giver_name,
        "reward_description": reward,
        "reward_xp": int(reward_xp),
        "reward_gold": int(reward_gold),
        # Progress / state fields
        "status": "active",
        "progress": 0,
        "rewarded": False,
    }


def format_quest_for_display(q: dict) -> str:
    """Turn a quest dict into a short readable line for the quest log."""
    if not q or not isinstance(q, dict):
        return ""
    desc = q.get("description", "Unknown task.")
    giver = q.get("quest_giver", "Someone")
    status = (q.get("status") or "active").lower()
    prefix = "[Completed] " if status == "completed" else ""
    return f"{prefix}[From {giver}] {desc}"
