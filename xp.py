from all_global_vars import all_global_vars
from user_db import get_user_by_id


def award_xp(userId, xp_amount):
    xp_amount = int(xp_amount)
    
    player_char = all_global_vars.get_player_character(userId)
    user_doc = get_user_by_id(userId)
    character_id = user_doc.get("_player_character_id")
    player_char.earned_exp(xp_amount)
    player_char.update_player_character(character_id)