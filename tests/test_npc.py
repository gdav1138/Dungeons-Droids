"""
Tests for NPC feature: player profile, interaction modifiers, and allow_pass/talk (mocked AI).
"""
import pytest
from unittest.mock import patch, MagicMock


class TestNpcPlayerProfile:
    """Tests for _player_profile (no API calls)."""

    def test_profile_includes_name_and_stats(self, userId):
        from npc import npc
        with patch("npc.all_global_vars") as mock_g:
            mock_pc = MagicMock()
            mock_pc._name = "Hero"
            mock_pc.get_stats.return_value = {"str": 3, "int": 3, "dex": 3, "cha": 3, "wis": 3, "con": 3}
            mock_pc.get_appearance.return_value = {"pronouns": "they/them", "summary": "Tall warrior"}
            mock_g.get_player_character.return_value = mock_pc
            with patch("npc.call_ai") as mock_ai:
                mock_ai.return_value = "TestNPC"
                n = npc(userId)
            profile = n._player_profile(userId)
            assert "Hero" in profile
            assert "STR" in profile or "str" in profile
            assert "they/them" in profile
            assert "Tall warrior" in profile

    def test_profile_handles_missing_name(self, userId):
        from npc import npc
        with patch("npc.all_global_vars") as mock_g:
            mock_pc = MagicMock()
            mock_pc._name = None
            mock_pc.get_stats.return_value = {"str": 0, "int": 0, "dex": 0, "cha": 0, "wis": 0, "con": 0}
            mock_pc.get_appearance.return_value = {}
            mock_g.get_player_character.return_value = mock_pc
            with patch("npc.call_ai") as mock_ai:
                mock_ai.return_value = "Stranger"
                n = npc(userId)
            profile = n._player_profile(userId)
            assert "the player" in profile or "Stranger" in profile


class TestNpcInteractionModifiers:
    """Tests for _interaction_modifiers (pure math, no AI)."""

    def test_modifiers_structure_and_agility(self, userId):
        from npc import npc
        with patch("npc.all_global_vars") as mock_g:
            mock_pc = MagicMock()
            mock_pc.get_stats.return_value = {
                "str": 5, "int": 5, "dex": 5, "cha": 5, "wis": 5, "con": 5,
            }
            mock_g.get_player_character.return_value = mock_pc
            with patch("npc.call_ai") as mock_ai:
                mock_ai.return_value = "TestNPC"
                n = npc(userId)
            mods = n._interaction_modifiers(userId)
            assert "persuasion" in mods
            assert "intimidation" in mods
            assert "awareness" in mods
            assert "agility" in mods
            assert mods["agility"] == 5
            assert 0 <= mods["persuasion"] <= 20

    def test_allow_pass_yes_from_ai(self, userId):
        from npc import npc
        with patch("npc.all_global_vars") as mock_g:
            mock_pc = MagicMock()
            mock_pc.get_stats.return_value = {"str": 5, "int": 5, "dex": 5, "cha": 5, "wis": 5, "con": 5}
            mock_pc.get_appearance.return_value = {}
            mock_g.get_player_character.return_value = mock_pc
            with patch("npc.call_ai") as mock_ai:
                mock_ai.return_value = "Yes"
                n = npc(userId)
                result = n.allow_pass(userId)
            assert result is True

    def test_allow_pass_no_from_ai(self, userId):
        from npc import npc
        with patch("npc.all_global_vars") as mock_g:
            mock_pc = MagicMock()
            mock_pc.get_stats.return_value = {"str": 1, "int": 1, "dex": 1, "cha": 1, "wis": 1, "con": 1}
            mock_pc.get_appearance.return_value = {}
            mock_g.get_player_character.return_value = mock_pc
            with patch("npc.call_ai") as mock_ai:
                mock_ai.return_value = "No"
                n = npc(userId)
                result = n.allow_pass(userId)
            assert result is False
