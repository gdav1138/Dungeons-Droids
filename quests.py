"""
Quest system: quest types and random quest generation.
Quests are stored as dicts for easy serialization; completion is not implemented in this build.
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
    Create a random quest appropriate for the theme. Returns a quest dict with:
    id, type, target, description, quest_giver, reward_description.
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
        reward = "a reward fitting your bravery"

    elif quest_type == QUEST_OBTAIN_ITEM:
        item_name = random.choice(QUEST_ITEMS)
        description = (
            f"Find and bring back a {item_name}. "
            f"Theme: {theme}. They need it for their own reasons."
        )
        target = item_name
        reward = "payment and their gratitude"

    else:  # QUEST_OBTAIN_GOLD
        amount = random.choice([50, 100, 200, 500])
        description = (
            f"Obtain {amount} gold (or equivalent currency) and deliver it. "
            f"Theme: {theme}. They have a debt to settle."
        )
        target = amount
        reward = "a share of the proceeds and a favor"

    return {
        "id": quest_id,
        "type": quest_type,
        "target": target,
        "description": description,
        "quest_giver": quest_giver_name,
        "reward_description": reward,
    }


def format_quest_for_display(q: dict) -> str:
    """Turn a quest dict into a short readable line for the quest log."""
    if not q or not isinstance(q, dict):
        return ""
    desc = q.get("description", "Unknown task.")
    giver = q.get("quest_giver", "Someone")
    return f"[From {giver}] {desc}"
