# The main gameplay loop. It has access to all the global variables, and has
# the input the user typed in (userInput) and has to return a string that it
# wants to display to the user. A few commands have been implemented as
# examples.

from all_global_vars import all_global_vars


def do_main_loop(userInput, userId):
    userInput = userInput.lower()
    # Handle empty/None input by showing current room
    if userInput == "none" or userInput == "":
        return all_global_vars.get_room_holder(userId).get_full_description(
            userId
        )
    if userInput == "restart":
        all_global_vars.set_section(userId, "Restart")
        return "Restarting Game. Type in anything to continue."
    if userInput == 'help':
        return (
            "Valid Commands:<BR>Restart - Restarts the game<BR>"
            + "Help - this menu<BR>"
            + "north, south, east, west - Move to a new location<BR>"
            + "describe npc - describes the npc in the room<BR>"
        )

    # Prepare current room_array for user action
    room_array = all_global_vars.get_player_character(userId).get_room_array()
    if userInput == 'look':
        return room_array.get_full_description(userId)
    if userInput == 'north':
        response = room_array.move_north(userId)
        room_array.persist_room(userId, all_global_vars.get_player_character(userId))
        return response
    if userInput == 'south':
        response = room_array.move_south(userId)
        room_array.persist_room(userId, all_global_vars.get_player_character(userId))
        return response
    if userInput == 'east':
        response = room_array.move_east(userId)
        room_array.persist_room(userId, all_global_vars.get_player_character(userId))
        return response
    if userInput == 'west':
        response = room_array.move_west(userId)
        room_array.persist_room(userId, all_global_vars.get_player_character(userId))
        return response
    if userInput == "describe npc":
        return room_array.describe_npc(userId)
    if userInput.startswith("say"):
        return room_array.talk_to_npc(userId, userInput[3:])
    
    return "Invalid input. Type help for options."
