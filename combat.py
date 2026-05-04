import random


VALID_COMBAT_ACTIONS = {"attack", "heavy", "defend", "flee"}


def _to_int(value, default=0):
    try:
        return int(value)
    except Exception:
        return default


def get_stat(character, stat_name):
    try:
        stats = character.get_stats()
    except Exception:
        stats = {}
    return _to_int(stats.get(stat_name, getattr(character, f"_{stat_name}", 0) or 0))


def get_equipment_bonus(character, bonus_name):
    try:
        return _to_int(character.get_equipment_bonus(bonus_name))
    except Exception:
        return 0


def max_player_health(player_char):
    level = _to_int(getattr(player_char, "_level", 1), 1)
    con = get_stat(player_char, "con")
    return 100 + (level - 1) * 10 + con * 5


def max_npc_health(npc):
    level = _to_int(getattr(npc, "_level", 1), 1)
    toughness = _to_int(getattr(npc, "_toughness", 50), 50)
    return 35 + level * 5 + toughness // 2


def ensure_combat_health(player_char, npc):
    player_max = max_player_health(player_char)
    npc_max = max_npc_health(npc)

    if getattr(player_char, "_health", None) is None or _to_int(player_char._health) <= 0:
        player_char._health = player_max
    else:
        player_char._health = min(_to_int(player_char._health), player_max)

    if getattr(npc, "_health", None) is None or _to_int(npc._health) <= 0:
        npc._health = npc_max
    else:
        npc._health = min(_to_int(npc._health), npc_max)

    return player_max, npc_max


def resolve_combat_turn(player_char, npc, action, rng=None):
    rng = rng or random
    action = (action or "attack").strip().lower()
    if action == "heavy attack":
        action = "heavy"
    if action not in VALID_COMBAT_ACTIONS:
        action = "attack"

    player_max, npc_max = ensure_combat_health(player_char, npc)

    str_ = get_stat(player_char, "str")
    dex = get_stat(player_char, "dex")
    wis = get_stat(player_char, "wis")
    con = get_stat(player_char, "con")
    weapon_bonus = get_equipment_bonus(player_char, "damage")
    armor_bonus = get_equipment_bonus(player_char, "armor")
    toughness = _to_int(getattr(npc, "_toughness", 50), 50)

    result = {
        "action": action,
        "player_hit": False,
        "player_damage": 0,
        "npc_damage": 0,
        "fled": False,
        "defended": action == "defend",
        "player_defeated": False,
        "npc_defeated": False,
        "player_health": _to_int(player_char._health),
        "player_max_health": player_max,
        "npc_health": _to_int(npc._health),
        "npc_max_health": npc_max,
        "message": "",
    }

    if action == "flee":
        flee_chance = min(85, max(15, 35 + dex * 4 + wis * 2 - toughness // 5))
        result["flee_chance"] = flee_chance
        if rng.randint(1, 100) <= flee_chance:
            result["fled"] = True
            result["message"] = "You break away from the fight."
            return result
        result["message"] = "You try to flee, but the enemy keeps pressure on you."

    if action in ("attack", "heavy"):
        if action == "heavy":
            hit_chance = min(90, 45 + dex * 2)
            damage = rng.randint(8, 14) + str_ * 2 + weapon_bonus * 2
        else:
            hit_chance = min(95, 65 + dex * 3)
            damage = rng.randint(4, 8) + str_ + weapon_bonus

        result["hit_chance"] = hit_chance
        if rng.randint(1, 100) <= hit_chance:
            damage = max(1, damage)
            npc._health = max(0, _to_int(npc._health) - damage)
            result["player_hit"] = True
            result["player_damage"] = damage
        else:
            result["message"] = "Your attack misses."

    if action == "defend":
        result["message"] = "You brace for the next blow."

    if _to_int(npc._health) <= 0:
        result["npc_defeated"] = True
    else:
        npc_damage = rng.randint(4, 10) + toughness // 12
        npc_damage -= con // 2
        npc_damage -= armor_bonus
        if action == "defend":
            npc_damage = npc_damage // 2
        npc_damage = max(0, npc_damage)
        player_char._health = max(0, _to_int(player_char._health) - npc_damage)
        result["npc_damage"] = npc_damage

    if _to_int(player_char._health) <= 0:
        result["player_defeated"] = True

    result["player_health"] = _to_int(player_char._health)
    result["npc_health"] = _to_int(npc._health)
    return result
