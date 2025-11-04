from open_ai_api import call_ai
from all_global_vars import all_global_vars

class Room:
    def __init__(self):
        self._description = "Not Generated Yet"
        self._visited = False

    def generate_description(self, userId):
        client_response = ""
        setup_string = "Make up a location or MUD room description fitting the theme " + all_global_vars.get_theme(userId)._era + " for a character named " + all_global_vars.get_player_character(userId).get_name() + ". Don't list any exits or items or anything other than a description of a location. Make it about 3 sentences."
        client_response += call_ai(setup_string) + "\n"
        self._description = client_response
        self._visited = True

class room_holder:
    def __init__(self):
        self._rows = 3
        self._cols = 4
        self._array_of_rooms = [[None for _ in range(self._cols)] for _ in range(self._rows)]
        self._cur_pos_x = 0
        self._cur_pos_y = 0
    
    def add_empty_room(self, x_row, y_col):
        print(f"Added empty room at x_row: {x_row}, y_col: {y_col}")
        self._array_of_rooms[y_col][x_row] = Room()

    def get_room(self, x_row, y_col):
        return self._array_of_rooms[y_col][x_row]
    
    def get_current_room(self):
        return self._array_of_rooms[self._cur_pos_y][self._cur_pos_x]
    
    def get_exits(self):
        cur_x = self._cur_pos_x
        cur_y = self._cur_pos_y
        arr = self._array_of_rooms
        
        ret_string = "Exits: "
        print(f"cur_x: {cur_x}, cur_y: {cur_y}")
        print("Exits: ")
        if self._cols > cur_y + 1:
            if arr[cur_y+1][cur_x] != None:
                ret_string += "North "
        if cur_y > 0:
            if arr[cur_y-1][cur_x] != None:
                ret_string += "South "
        if self._rows > cur_x + 1:
            if arr[cur_y][cur_x+1] != None:
                ret_string += "East "
        if cur_x > 0:
            if arr[cur_y][cur_x-1] != None:
                ret_string += "West "

        return ret_string

    def get_full_description(self, userId):
        print(f"Getting full desc for {self._cur_pos_x}, {self._cur_pos_y}")
        
        if self.get_current_room() == None:
            return "Error: Tried to describe a None room."
        if self.get_current_room()._visited == False:
            self.get_current_room().generate_description(userId)
        
        ret_string = ""
        ret_string += self.get_current_room()._description
        ret_string += "<BR>"
        ret_string += self.get_exits()
        return ret_string
    
    def move_north(self, userId):
        cur_x = self._cur_pos_x
        cur_y = self._cur_pos_y
        arr = self._array_of_rooms
        
        if self._cols > cur_y + 1:
            if arr[cur_y+1][cur_x] != None:
                self._cur_pos_y += 1
                return self.get_full_description(userId)
        
        return "Can't move that way!"
    
    def move_south(self, userId):
        cur_x = self._cur_pos_x
        cur_y = self._cur_pos_y
        arr = self._array_of_rooms
        
        if 0 <= cur_y - 1:
            if arr[cur_y-1][cur_x] != None:
                self._cur_pos_y -= 1
                return self.get_full_description(userId)
        
        return "Can't move that way!"