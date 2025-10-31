from all_global_vars import all_global_vars
from open_ai_api import call_ai

def do_main_loop(userInput, userId):
    userInput = userInput.lower()
    if userInput == "restart":
        all_global_vars.set_section(userId, "Restart")
        return "Restarting Game. Type in anything to continue."
    if userInput == 'help':
        return "Valid Commands:<BR>Restart - Restarts the game<BR>Help - this menu"
    else:
        return "Invalid input. Type help for options."