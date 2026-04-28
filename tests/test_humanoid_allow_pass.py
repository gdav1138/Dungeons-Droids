from unittest.mock import patch


def test_humanoid_npc_allow_pass_short_circuits_when_already_granted():
    # Construct Npc without running __init__ (which calls the LLM and touches DB).
    from humanoid import Npc

    n = object.__new__(Npc)
    n._friendlyness = 50
    n._past_conversation = [
        "Note: The player bribed the NPC with 10 gold and the NPC accepted, agreeing to let them pass."
    ]

    # If the short-circuit works, we should never call the LLM.
    with patch("humanoid.call_ai") as mock_ai:
        mock_ai.side_effect = AssertionError("call_ai should not be called when passage is granted")
        assert n.allow_pass("user") is True

