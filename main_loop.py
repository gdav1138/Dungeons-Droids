# The main gameplay loop. It has access to all the global variables, and has
# the input the user typed in (userInput) and has to return a string that it
# wants to display to the user. A few commands have been implemented as
# examples.

from all_global_vars import all_global_vars


def do_main_loop(userInput, userId):
    userInput = userInput.lower()
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
    if userInput == 'look':
        return all_global_vars.get_room_holder(userId).get_full_description(
            userId
        )
    if userInput == 'north':
        return all_global_vars.get_room_holder(userId).move_north(userId)
    if userInput == 'south':
        return all_global_vars.get_room_holder(userId).move_south(userId)
    if userInput == 'east':
        return all_global_vars.get_room_holder(userId).move_east(userId)
    if userInput == 'west':
        return all_global_vars.get_room_holder(userId).move_west(userId)
    if userInput == "describe npc":
        return all_global_vars.get_room_holder(userId).describe_npc(userId)
    if userInput.startswith("say"):
        return all_global_vars.get_room_holder(userId).talk_to_npc(userId, userInput[3:])
    
    return "Invalid input. Type help for options."
