from humanoid import PlayerCharacter
from quests import QUEST_DEFEAT_ENEMIES


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

