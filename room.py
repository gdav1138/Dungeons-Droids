from open_ai_api import call_ai
from all_global_vars import all_global_vars
from map_generator import generate_room_map
from npc import npc
from item import Item, generate_random_item
import random

class Room:
    def __init__(self):
        self._description = "Not Generated Yet"
        self._visited = False
        self._map_html = None
        self._npc = None
        self._items = []  # List of Item objects in the room

    def generate_description(self, userId):
        self._npc = npc(userId)
        client_response = ""
        setup_string = "Make up a location or MUD room description fitting the theme " + all_global_vars.get_theme(
            userId)._era + " for a character named " + all_global_vars.get_player_character(
            userId).get_name() + ". Don't list any exits or items or anything other than a description of a location."
        if self._npc is not None:
            setup_string += "Include a mention of an NPC named " + self._npc._name + " and subtlely include the description " + self._npc._description
        client_response += call_ai(setup_string) + "\n"
        self._description = client_response
        self._visited = True
        
        # Randomly add items to room (50% chance)
        if random.random() < 0.5:
            theme_era = all_global_vars.get_theme(userId)._era
            num_items = random.randint(1, 2)  # 1-2 items per room
            for _ in range(num_items):
                self._items.append(generate_random_item(theme_era))
    
    def add_item(self, item):
        """Add an item to the room"""
        self._items.append(item)
    
    def remove_item(self, item_name):
        """Remove and return an item from the room by name"""
        for item in self._items:
            if item.get_name().lower() == item_name.lower():
                self._items.remove(item)
                return item
        return None
    
    def get_items(self):
        """Get list of items in the room"""
        return self._items
    
    def has_items(self):
        """Check if room has any items"""
        return len(self._items) > 0


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
        if cur_y + 1 < self._rows:
            if arr[cur_y + 1][cur_x] != None:
                ret_string += "North "
        if cur_y > 0:
            if arr[cur_y - 1][cur_x] != None:
                ret_string += "South "
        if cur_x + 1 < self._cols:
            if arr[cur_y][cur_x + 1] != None:
                ret_string += "East "
        if cur_x > 0:
            if arr[cur_y][cur_x - 1] != None:
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
        ret_string += "<BR>"
        
        # Show items in the room
        if self.get_current_room().has_items():
            ret_string += "<BR>You see the following items here:<BR>"
            for item in self.get_current_room().get_items():
                ret_string += f"  - {item.get_name()} ({item.get_type()})<BR>"
        
        return ret_string
    
    def get_map_html(self, userId):
        """Get the map HTML separately from the description"""
        theme_era = all_global_vars.get_theme(userId)._era
        cur_room = self.get_current_room()
        if not getattr(cur_room, "_map_html", None):
            cur_room._map_html = generate_room_map(self, theme_era)
        return cur_room._map_html

    def get_minimap_html(self, userId):
        """Get the ASCII-style minimap for the whole dungeon"""
        return self.render_minimap()
    
    def describe_npc(self, userId):
        return self.get_current_room()._npc._name + " looks like " + self.get_current_room()._npc._description
    
    def talk_to_npc(self, userId, talk_string):
        return self.get_current_room()._npc.talk(userId, talk_string)
    
    def move_north(self, userId):
        cur_x = self._cur_pos_x
        cur_y = self._cur_pos_y
        arr = self._array_of_rooms

        if cur_y + 1 < self._rows:
            if arr[cur_y + 1][cur_x] != None:
                self._cur_pos_y += 1
                return self.get_full_description(userId)

        return "Can't move that way!"

    def move_south(self, userId):
        cur_x = self._cur_pos_x
        cur_y = self._cur_pos_y
        arr = self._array_of_rooms

        if 0 <= cur_y - 1:
            if arr[cur_y - 1][cur_x] != None:
                self._cur_pos_y -= 1
                return self.get_full_description(userId)

        return "Can't move that way!"

    def move_east(self, userId):
        """Move player to the east room if available"""
        cur_x = self._cur_pos_x
        cur_y = self._cur_pos_y
        arr = self._array_of_rooms

        if cur_x + 1 < self._cols:
            if arr[cur_y][cur_x + 1] is not None:
                self._cur_pos_x += 1
                return self.get_full_description(userId)

        return "Can't move that way!"

    def move_west(self, userId):
        """Move player to the west room if available"""
        cur_x = self._cur_pos_x
        cur_y = self._cur_pos_y
        arr = self._array_of_rooms

        if cur_x - 1 >= 0:
            if arr[cur_y][cur_x - 1] is not None:
                self._cur_pos_x -= 1
                return self.get_full_description(userId)

        return "Can't move that way!"

    def render_minimap(self):
        """Return an HTML snippet with an ASCII-style minimap of rooms.

        Legend:
        - [E] current position (blue)
        - [-] visited room (green)
        - [?] undiscovered but generated room (dim)
        Empty space means no room exists at that coordinate.
        """

        rows = self._rows
        cols = self._cols
        arr = self._array_of_rooms
        cx = self._cur_pos_x
        cy = self._cur_pos_y

        def cell_token(x, y):
            r = arr[y][x]
            if r is None:
                return '<span style="color:#333">···</span>'
            if x == cx and y == cy:
                return '<span style="color:#00d4ff;font-weight:bold">[●]</span>'
            if getattr(r, "_visited", False):
                return '<span style="color:#00ff88">[■]</span>'
            return '<span style="color:#666">[▢]</span>'

        lines = []
        # Render north (top) to south (bottom)
        for y in range(rows - 1, -1, -1):
            # cells row
            row_parts = []
            for x in range(cols):
                row_parts.append(cell_token(x, y))
                # horizontal connector between rooms
                if x < cols - 1:
                    if arr[y][x] is not None and arr[y][x + 1] is not None:
                        row_parts.append('<span style="color:#555">──</span>')
                    else:
                        row_parts.append('  ')
            lines.append(''.join(row_parts))

            # vertical connectors (skip after last printed row)
            if y > 0:
                conn_parts = []
                for x in range(cols):
                    if arr[y][x] is not None and arr[y - 1][x] is not None:
                        conn_parts.append(
                            ' '
                            '<span style="color:#555">│</span>'
                            ' '
                        )
                    else:
                        conn_parts.append('   ')
                    # keep spacing with horizontal gaps too
                    if x < cols - 1:
                        conn_parts.append('  ')
                lines.append(''.join(conn_parts))

        legend = (
            '<div style="margin-top:10px;font-size:11px;color:#999;letter-spacing:0.5px">'
            '<span style="color:#00d4ff;font-weight:bold">[●]</span> You  '
            '<span style="color:#00ff88">[■]</span> Visited  '
            '<span style="color:#666">[▢]</span> Unexplored  '
            '<span style="color:#555">─│</span> Connections'
            '</div>'
        )

        wrapper = (
            '<div style="border:1px solid #444;padding:12px;border-radius:4px;'
            'background:#1a1a1a;font-family:monospace">'
            + '<pre style="margin:0;line-height:1.5;font-size:14px">'
            + "\n".join(lines)
            + '</pre>'
            + legend
            + '</div>'
        )
        return wrapper
    
    def pickup_item(self, userId, item_name):
        """Pick up an item from the current room"""
        cur_room = self.get_current_room()
        item = cur_room.remove_item(item_name)
        
        if item:
            player = all_global_vars.get_player_character(userId)
            player.add_item(item)
            # Clear cached map so it regenerates without the item
            cur_room._map_html = None
            return f"You picked up: {item.get_name()}<BR>{item.get_description()}"
        else:
            return f"There is no '{item_name}' here to pick up."
    
    def drop_item(self, userId, item_name):
        """Drop an item from inventory into the current room"""
        player = all_global_vars.get_player_character(userId)
        item = player.remove_item(item_name)
        
        if item:
            cur_room = self.get_current_room()
            cur_room.add_item(item)
            # Clear cached map so it regenerates with the new item
            cur_room._map_html = None
            return f"You dropped: {item.get_name()}"
        else:
            return f"You don't have '{item_name}' in your inventory."
    
    def show_inventory(self, userId):
        """Show the player's inventory"""
        player = all_global_vars.get_player_character(userId)
        inventory = player.get_inventory()
        
        if not inventory:
            return "Your inventory is empty."
        
        ret_string = "Your inventory:<BR>"
        for item in inventory:
            ret_string += f"  - {item.get_name()} ({item.get_type()}) - {item.get_description()}<BR>"
        
        return ret_string
