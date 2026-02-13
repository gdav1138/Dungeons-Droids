# The main gameplay loop. It has access to all the global variables, and has
# the input the user typed in (userInput) and has to return a string that it
# wants to display to the user. A few commands have been implemented as
# examples.

from all_global_vars import all_global_vars
from quests import format_quest_for_display
import hello

def _format_inventory(inv_list):
    if not inv_list:
        return "Inventory: (empty)<BR>"
    lines = ["Inventory:"]
    for item in inv_list:
        lines.append(f"- {item}")
    return "<BR>".join(lines) + "<BR>"


def _brief_room_view(room_array, userId):
    """Return only map + minimap + item names (no long description)."""
    # Generate/refresh map and minimap
    room_array.get_full_description(userId)

    cur_room = room_array.get_current_room()
    parts = []
    if cur_room and getattr(cur_room, "_map_html", None):
        parts.append(cur_room._map_html)

    try:
        world = room_array.render_minimap()
        parts.append(f'<div data-role="worldmap">{world}</div>')
    except Exception:
        pass

    items = room_array.list_items() if hasattr(room_array, "list_items") else []

    def _iname(it):
        if isinstance(it, dict):
            return it.get("name", "")
        return str(it)

    if items:
        parts.append("Items here: " + ", ".join(_iname(i) for i in items))
    else:
        parts.append("Items here: none")

    return "<BR>".join(parts)


def do_main_loop(userInput, userId):
    userInput = userInput.lower()
    # Handle empty/None input by showing current room
    if userInput == "none" or userInput == "":
        return all_global_vars.get_player_character(userId).get_room_array().get_full_description(
            userId
        )
    if userInput == "restart":
        print("userInput == restart")
        return hello.restart_game(userId)
    if userInput == 'help':
        return (
            "Valid Commands:<BR>Restart - Restarts the game<BR>"
            + "Help - this menu<BR>"
            + "north, south, east, west - Move to a new location<BR>"
            + "describe npc - describes the npc in the room<BR>"
            + "inventory (i) - show your items<BR>"
            + "quests (q) - show your active quests<BR>"
            + "pickup/take <item> - pick up an item here<BR>"
            + "drop <item> - drop an item from inventory<BR>"
        )

    # Prepare current room_array for user action
    room_array = all_global_vars.get_player_character(userId).get_room_array()

    # Inventory view
    if userInput in ("inventory", "inv", "i"):
        inv = all_global_vars.get_player_character(userId).get_inventory()
        return _format_inventory(inv)

    # Quest log
    if userInput in ("quests", "q"):
        quest_list = all_global_vars.get_player_character(userId).get_quests()
        if not quest_list:
            return "Active quests: (none)<BR>"
        lines = ["Active quests:"]
        for q in quest_list:
            lines.append("- " + format_quest_for_display(q))
        return "<BR>".join(lines) + "<BR>"

    # Prepare current room_array for user action
    player_char = all_global_vars.get_player_character(userId)
    room_array = player_char.get_room_array()

    # Pick up
    for prefix in ("take ", "pickup ", "pick up ", "grab "):
        if userInput.startswith(prefix):
            item = userInput[len(prefix):].strip()
            if not item:
                return "Specify what to pick up.<BR>"
            success, info = room_array.pickup_item(item, player_char)
            if success:
                room_array.persist_room(userId, player_char)
                from user_db import get_user_by_id

                user_doc = get_user_by_id(userId)
                char_id = user_doc.get("_player_character_id") if user_doc else None
                if char_id:
                    player_char.update_player_character(char_id)
                refreshed = _brief_room_view(room_array, userId)
                return f"You picked up {info}.<BR>{refreshed}"
            return info + "<BR>"

    # Drop
    if userInput.startswith("drop "):
        item = userInput[len("drop "):].strip()
        if not item:
            return "Specify what to drop.<BR>"
        success, info = room_array.drop_item(item, player_char)
        if success:
            room_array.persist_room(userId, player_char)
            from user_db import get_user_by_id

            user_doc = get_user_by_id(userId)
            char_id = user_doc.get("_player_character_id") if user_doc else None
            if char_id:
                player_char.update_player_character(char_id)
            refreshed = _brief_room_view(room_array, userId)
            return f"You dropped {info}.<BR>{refreshed}"
        return info + "<BR>"
    if userInput == 'look':
        return room_array.get_full_description(userId)
    if userInput == 'north':
        if room_array.get_current_room()._npc is None:
            okay_to_move = True
            npc_response = "There is no NPC in this room."
        else:
            okay_to_move, npc_response = check_direction_for_npc(userId, room_array)
        if okay_to_move:
            response = room_array.move_north(userId)
            room_array.persist_room(userId, all_global_vars.get_player_character(userId))
            return npc_response + "<BR>" + response
        else:
            return npc_response
    if userInput == 'south':
        if room_array.get_current_room()._npc is None:
            okay_to_move = True
            npc_response = "There is no NPC in this room."
        else:
            okay_to_move, npc_response = check_direction_for_npc(userId, room_array)
        if okay_to_move:
            response = room_array.move_south(userId)
            room_array.persist_room(userId, all_global_vars.get_player_character(userId))
            return npc_response + "<BR>" + response
        else:
            return npc_response
    if userInput == 'east':
        if room_array.get_current_room()._npc is None:
            okay_to_move = True
            npc_response = "There is no NPC in this room."
        else:
            okay_to_move, npc_response = check_direction_for_npc(userId, room_array)
        if okay_to_move:
            response = room_array.move_east(userId)
            room_array.persist_room(userId, all_global_vars.get_player_character(userId))
            return npc_response + "<BR>" + response
        else:
            return npc_response
    if userInput == 'west':
        if room_array.get_current_room()._npc is None:
            okay_to_move = True
            npc_response = "There is no NPC in this room."
        else:
            okay_to_move, npc_response = check_direction_for_npc(userId, room_array)
        if okay_to_move:
            response = room_array.move_west(userId)
            room_array.persist_room(userId, all_global_vars.get_player_character(userId))
            return npc_response + "<BR>" + response
        else:
            return npc_response
    if userInput == "describe npc":
        return room_array.describe_npc(userId)
    if userInput.startswith("say"):
        return room_array.talk_to_npc(userId, userInput[3:])
    if userInput.startswith("version"):
        return all_global_vars.get_version()
    
    return "Invalid input. Type help for options."

def check_direction_for_npc(userId, room_array):
    print("1")
    print("room_array: ", room_array)
    print("2")
    try:
        can_pass = room_array.check_pass_npc(userId)
    except Exception as e:
        print("ERROR in check_pass_npc:", repr(e))
        raise
    #can_pass = room_array.check_pass_npc(userId)
    print("Can pass: " + str(can_pass))
    if can_pass:
        return True, "The NPC lets you exit the room"
    else:
        return False, "The NPC blocks your exit"