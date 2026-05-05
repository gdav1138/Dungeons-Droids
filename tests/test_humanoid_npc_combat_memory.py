from unittest.mock import MagicMock, patch


def _npc_without_init():
    from humanoid import Humanoid, Npc

    npc = Npc.__new__(Npc)
    Humanoid.__init__(npc)
    npc._id = "npc-id"
    npc._name = "Rusk"
    npc._description = "a wary guard"
    npc._friendlyness = 20
    npc._toughness = 40
    npc._past_conversation = [
        "Combat note: The player used a quick attack against Rusk. "
        "The player dealt 8 damage. Rusk dealt 4 damage."
    ]
    npc._quest_to_offer = None
    return npc


def test_talk_prompt_reflects_combat_history(userId):
    npc = _npc_without_init()

    with patch("humanoid.call_ai", return_value="You have nerve coming back to parley.") as mock_ai:
        with patch.object(npc, "update_npc", return_value=MagicMock()):
            with patch("xp.award_xp"):
                out = npc.talk(userId, "Can we talk?")

    prompt = mock_ai.call_args.args[0]
    assert "Combat note" in prompt
    assert "quick attack" in prompt
    assert "react with appropriate fear, anger, caution" in prompt
    assert "Rusk says" in out
