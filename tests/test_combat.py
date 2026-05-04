from types import SimpleNamespace


class FakeRng:
    def __init__(self, values):
        self.values = list(values)

    def randint(self, _low, _high):
        return self.values.pop(0)


class FakePlayer:
    def __init__(self):
        self._level = 1
        self._health = 100
        self._stats = {"str": 4, "int": 0, "dex": 4, "cha": 0, "wis": 3, "con": 4}

    def get_stats(self):
        return dict(self._stats)

    def get_equipment_bonus(self, bonus_name):
        return {"damage": 2, "armor": 1}.get(bonus_name, 0)


def test_attack_damages_npc_and_triggers_counterattack():
    from combat import resolve_combat_turn

    player = FakePlayer()
    npc = SimpleNamespace(_level=1, _health=60, _toughness=40)

    result = resolve_combat_turn(player, npc, "attack", rng=FakeRng([6, 1, 8]))

    assert result["player_hit"] is True
    assert result["player_damage"] == 12
    assert result["npc_health"] == 48
    assert result["npc_damage"] == 8
    assert result["player_health"] == 92


def test_defend_reduces_incoming_damage():
    from combat import resolve_combat_turn

    player = FakePlayer()
    npc = SimpleNamespace(_level=1, _health=60, _toughness=40)

    result = resolve_combat_turn(player, npc, "defend", rng=FakeRng([8]))

    assert result["defended"] is True
    assert result["player_damage"] == 0
    assert result["npc_damage"] == 4
    assert result["player_health"] == 96


def test_successful_flee_skips_counterattack():
    from combat import resolve_combat_turn

    player = FakePlayer()
    npc = SimpleNamespace(_level=1, _health=60, _toughness=40)

    result = resolve_combat_turn(player, npc, "flee", rng=FakeRng([1]))

    assert result["fled"] is True
    assert result["npc_damage"] == 0
    assert result["player_health"] == 100
