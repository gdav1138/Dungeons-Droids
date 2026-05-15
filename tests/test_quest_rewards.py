from humanoid import PlayerCharacter
from quests import QUEST_DEFEAT_ENEMIES, QUEST_OBTAIN_ITEM


def test_quest_completion_awards_xp_and_gold_once():
    pc = PlayerCharacter()

    q = {
        "id": "test-quest-1",
        "type": QUEST_DEFEAT_ENEMIES,
        "target": 1,
        "description": "Defeat 1 enemy.",
        "quest_giver": "Tester",
        "reward_description": "25 XP and 10 gold",
        "reward_xp": 25,
        "reward_gold": 10,
        "status": "active",
        "progress": 0,
        "rewarded": False,
    }

    pc.add_quest(q)
    assert pc.get_current_exp() == 0
    assert pc.get_gold() == 0

    pc.record_enemy_kill(1)

    quests = pc.get_quests()
    assert quests[0]["status"] == "completed"
    assert quests[0]["rewarded"] is True
    assert pc.get_current_exp() == 25
    assert pc.get_gold() == 10

    # Calling again shouldn't double-pay.
    pc.record_enemy_kill(1)
    assert pc.get_current_exp() == 25
    assert pc.get_gold() == 10


def test_collect_n_items_quest_counts_any_pickup():
    pc = PlayerCharacter()
    q = {
        "id": "test-quest-items",
        "type": QUEST_OBTAIN_ITEM,
        "target": 3,
        "description": "Pick up 3 items.",
        "quest_giver": "Tester",
        "reward_description": "12 XP and 9 gold",
        "reward_xp": 12,
        "reward_gold": 9,
        "status": "active",
        "progress": 0,
        "rewarded": False,
    }
    pc.add_quest(q)

    pc.record_item_obtained({"name": "Apple"})
    pc.record_item_obtained({"name": "Bolt"})
    assert pc.get_quests()[0]["status"] == "active"
    assert pc.get_quests()[0]["progress"] == 2

    pc.record_item_obtained({"name": "Cog"})
    assert pc.get_quests()[0]["status"] == "completed"
    assert pc.get_quests()[0]["rewarded"] is True
    assert pc.get_current_exp() == 12
    assert pc.get_gold() == 9

