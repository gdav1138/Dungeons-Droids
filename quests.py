"""
Quest system: quest types and random quest generation.

Each quest is stored as a plain dict so it can be easily serialized into MongoDB and
rehydrated back into a player character.

    {
        "id": <str uuid>,
        "type": <one of QUEST_*>,
        "target": <int|str>,    # e.g. kill count, item name, gold amount
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
- obtain_item: quest is complete when the matching item is obtained once.
- obtain_gold: quest is complete when the player's gold >= target.
"""
import random
import uuid

# Quest type constants
QUEST_DEFEAT_ENEMIES = "defeat_enemies"
QUEST_OBTAIN_ITEM = "obtain_item"
QUEST_OBTAIN_GOLD = "obtain_gold"

# Item names that can be requested (overlap with room loot where possible)
QUEST_ITEMS = [
    "rusty dagger", "leather satchel", "bronze coin", "torch", "old map",
    "copper key", "medkit", "data shard", "plasma cell", "gear fragment",
    "rations", "rope", "gemstone", "ancient scroll", "oil flask",
    "metal scrap", "sealed vial",
]


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
        count = random.choice([3, 5, 7, 10])
        description = (
            f"Defeat {count} enemies or monsters. "
            f"Theme: {theme}. Return when the task is done."
        )
        target = count
        reward_xp = 20 * count
        reward_gold = 10 * count
        reward = f"{reward_xp} XP and {reward_gold} gold"

    elif quest_type == QUEST_OBTAIN_ITEM:
        item_name = random.choice(QUEST_ITEMS)
        description = (
            f"Find and bring back a {item_name}. "
            f"Theme: {theme}. They need it for their own reasons."
        )
        target = item_name
        reward_xp = 60
        reward_gold = 75
        reward = f"{reward_xp} XP and {reward_gold} gold"

    else:  # QUEST_OBTAIN_GOLD
        amount = random.choice([50, 100, 200, 500])
        description = (
            f"Obtain {amount} gold (or equivalent currency) and deliver it. "
            f"Theme: {theme}. They have a debt to settle."
        )
        target = amount
        reward_xp = 50
        reward_gold = max(10, int(amount * 0.2))
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
