"""
Tests for Character Player Creator: player_character model and hello.py creation flow
(name, pronouns, appearance, stats, confirmation)
"""
import pytest
from unittest.mock import patch, MagicMock


# ---- player_character (model) ----

class TestPlayerCharacterModel:
    """player_character in-memory behavior used by the creator."""

    def test_get_stats_default_none_to_zero(self):
        from player_character import player_character
        pc = player_character()
        stats = pc.get_stats()
        assert stats["str"] == 0 and stats["int"] == 0 and stats["con"] == 0

    def test_set_name_and_get_name(self):
        from player_character import player_character
        pc = player_character()
        pc.set_name("Aria")
        assert pc.get_name() == "Aria"

    def test_set_pronouns_and_appearance_summary(self):
        from player_character import player_character
        pc = player_character()
        pc.set_pronouns("they/them")
        pc.set_appearance_summary("Tall with red hair")
        app = pc.get_appearance()
        assert app["pronouns"] == "they/them"
        assert app["summary"] == "Tall with red hair"

    def test_set_appearance_field_valid_keys(self):
        from player_character import player_character
        pc = player_character()
        pc.set_appearance_field("hair", "black")
        assert pc.get_appearance()["hair"] == "black"

    def test_set_appearance_field_invalid_key_raises(self):
        from player_character import player_character
        pc = player_character()
        with pytest.raises(ValueError, match="Invalid appearance key"):
            pc.set_appearance_field("invalid", "x")

    def test_stats_stored_and_returned(self):
        from player_character import player_character
        pc = player_character()
        pc._str, pc._int, pc._dex = 4, 4, 4
        pc._cha, pc._wis, pc._con = 2, 2, 4
        stats = pc.get_stats()
        assert stats["str"] == 4 and stats["con"] == 4

    def test_level_up_and_earned_exp_over_100(self):
        from player_character import player_character
        pc = player_character()
        pc._str = pc._int = pc._dex = pc._cha = pc._wis = pc._con = 0
        pc.set_exp(0)
        pc.earned_exp(100)
        assert pc._level == 2
        assert pc.get_current_exp() == 0


# ---- hello.py character creation handlers ----

class TestDoGetPlayerName:
    def test_empty_name_returns_error(self, userId):
        import hello
        with patch("hello.all_global_vars") as mock_g:
            mock_g.get_player_character.return_value = MagicMock()
            out = hello.doGetPlayerName("   ", userId)
            assert "valid name" in out.lower()

    def test_valid_name_sets_section_and_returns_welcome(self, userId):
        import hello
        with patch("hello.all_global_vars") as mock_g, patch("hello.user_db") as mock_db:
            mock_char = MagicMock()
            mock_g.get_player_character.return_value = mock_char
            mock_db.get_user_by_id.return_value = {"_player_character_id": "cid"}
            out = hello.doGetPlayerName("Alice", userId)
            mock_char.set_name.assert_called_once_with("Alice")
            mock_char.set_section.assert_called_once_with(section="GetPlayerPronouns")
            assert "Alice" in out and "Welcome" in out


class TestDoGetPlayerPronouns:
    def test_skip_advances_section(self, userId):
        import hello
        with patch("hello.all_global_vars") as mock_g:
            mock_char = MagicMock()
            mock_g.get_player_character.return_value = mock_char
            out = hello.doGetPlayerPronouns("skip", userId)
            mock_char.set_section.assert_called_with(section="GetPlayerAppearance")
            assert "appearance" in out.lower() or "sentence" in out.lower()

    def test_pronouns_stored_when_not_skip(self, userId):
        import hello
        with patch("hello.all_global_vars") as mock_g, patch("hello.user_db") as mock_db:
            mock_char = MagicMock()
            mock_g.get_player_character.return_value = mock_char
            mock_db.get_user_by_id.return_value = {"_player_character_id": "cid"}
            out = hello.doGetPlayerPronouns("they/them", userId)
            mock_char.set_pronouns.assert_called_once_with("they/them")
            mock_char.set_section.assert_called_with(section="GetPlayerAppearance")


class TestDoGetPlayerAppearance:
    def test_skip_advances_to_strength(self, userId):
        import hello
        with patch("hello.all_global_vars") as mock_g:
            mock_char = MagicMock()
            mock_g.get_player_character.return_value = mock_char
            out = hello.doGetPlayerAppearance("skip", userId)
            mock_char.set_section.assert_called_with(section="GetPlayerStrength")
            assert "20" in out and "Strength" in out


class TestDoGetPlayerStrength:
    def test_negative_rejected(self, userId):
        import hello
        with patch("hello.all_global_vars") as mock_g:
            mock_g.get_player_character.return_value = MagicMock()
            out = hello.doGetPlayerStrength("-1", userId)
            assert "negative" in out.lower() or "0 and 10" in out

    def test_over_10_rejected(self, userId):
        import hello
        with patch("hello.all_global_vars") as mock_g:
            mock_g.get_player_character.return_value = MagicMock()
            out = hello.doGetPlayerStrength("11", userId)
            assert "exceed" in out.lower() or "0 and 10" in out

    def test_valid_advances_to_intelligence(self, userId):
        import hello
        with patch("hello.all_global_vars") as mock_g:
            mock_char = MagicMock()
            mock_g.get_player_character.return_value = mock_char
            out = hello.doGetPlayerStrength("5", userId)
            assert mock_char._str == 5
            mock_char.set_section.assert_called_with(section="GetPlayerIntelligence")
            assert "Intelligence" in out

    def test_non_numeric_returns_error(self, userId):
        import hello
        with patch("hello.all_global_vars") as mock_g:
            mock_g.get_player_character.return_value = MagicMock()
            out = hello.doGetPlayerStrength("abc", userId)
            assert "valid number" in out.lower()


class TestDoGetPlayerConstitution:
    def test_total_not_20_resets_to_strength(self, userId):
        import hello
        with patch("hello.all_global_vars") as mock_g:
            mock_char = MagicMock()
            mock_char._str = mock_char._int = 5
            mock_char._dex = mock_char._cha = mock_char._wis = 2
            mock_char._con = None
            mock_g.get_player_character.return_value = mock_char
            out = hello.doGetPlayerConstitution("3", userId)
            assert "exactly 20" in out or "total is 19" in out
            mock_char.set_section.assert_called_with(section="GetPlayerStrength")

    def test_total_20_advances_to_confirm(self, userId):
        import hello
        with patch("hello.all_global_vars") as mock_g:
            mock_char = MagicMock()
            mock_char._str = mock_char._int = mock_char._dex = 4
            mock_char._cha = mock_char._wis = 3
            mock_char._con = None
            mock_g.get_player_character.return_value = mock_char
            out = hello.doGetPlayerConstitution("2", userId)
            assert mock_char._con == 2
            mock_char.set_section.assert_called_with(section="ConfirmPlayerStats")
            assert "yes" in out.lower() and "no" in out.lower()


class TestDoConfirmPlayerStats:
    def test_no_reprompts_strength(self, userId):
        import hello
        with patch("hello.all_global_vars") as mock_g:
            mock_char = MagicMock()
            mock_g.get_player_character.return_value = mock_char
            out = hello.doConfirmPlayerStats("no", userId)
            mock_char.set_section.assert_called_with(section="GetPlayerStrength")
            assert "Strength" in out

    def test_invalid_reprompts_confirm(self, userId):
        import hello
        with patch("hello.all_global_vars") as mock_g:
            mock_g.get_player_character.return_value = MagicMock()
            out = hello.doConfirmPlayerStats("maybe", userId)
            assert "yes" in out.lower() and "no" in out.lower()
