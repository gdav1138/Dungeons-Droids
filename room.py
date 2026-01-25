import random
import user_db
from open_ai_api import call_ai
from all_global_vars import all_global_vars
from map_generator import generate_room_map
from npc import npc

class Room:
    def __init__(self):
        self._description = "Not Generated Yet"
        self._visited = False
        self._map_html = None
        self._npc = None
        self._items = []

    def generate_description(self, userId):
        self._npc = npc(userId)
        client_response = ""
        setup_string = ("Make up a location or MUD room description fitting the theme "
                        + all_global_vars.get_player_character(userId).get_theme()
                        + " for a character named "
                        + all_global_vars.get_player_character(userId).get_name()
                        + ". Don't list any exits or items or anything other than a description of a location.")
        if self._npc is not None:
            setup_string += "Include a mention of an NPC named " + self._npc._name + " and subtlely include the description " + self._npc._description
        client_response += call_ai(setup_string) + "\n"
        self._description = client_response
        self._visited = True

        # Seed deterministic room loot based on position/description
        seed_key = getattr(self, "_seed", None)
        if seed_key is None:
            seed_key = random.randint(1, 999999)
            self._seed = seed_key
        random.seed(seed_key)

        base_items = [
            ("rusty dagger", "A pitted blade with a worn leather grip."),
            ("leather satchel", "A weathered satchel with a broken clasp."),
            ("bronze coin", "Ancient coin, its face worn smooth."),
            ("torch", "Wrapped in pitch-soaked cloth."),
            ("old map", "Faded parchment with partial routes."),
            ("copper key", "Small key etched with runes."),
            ("medkit", "Sterile wraps and coagulant foam."),
            ("data shard", "Encrypted storage crystal."),
            ("plasma cell", "Hums faintly with charge."),
            ("gear fragment", "Jagged cog from a larger machine."),
            ("rations", "Dry but filling travel food."),
            ("rope", "Coiled hemp rope, 30ft."),
            ("gemstone", "Uncut gem catching stray light."),
            ("ancient scroll", "Sealed with brittle wax."),
            ("oil flask", "Stoppered flask of lamp oil."),
            ("metal scrap", "Useful for patchwork repairs."),
            ("sealed vial", "Opaque fluid, cool to touch."),
        ]

        rarity_table = [
            ("Common", 1.0),
            ("Uncommon", 0.4),
            ("Rare", 0.18),
            ("Epic", 0.08),
            ("Legendary", 0.02),
        ]

        def pick_rarity():
            r = random.random()
            acc = 0.0
            for name, prob in rarity_table:
                acc += prob
                if r <= acc:
                    return name
            return "Common"

        def item_value(rarity):
            base = {
                "Common": (1, 8),
                "Uncommon": (10, 30),
                "Rare": (40, 120),
                "Epic": (150, 400),
                "Legendary": (500, 1200),
            }.get(rarity, (1, 8))
            return random.randint(*base)

        item_count = random.randint(2, 4)
        chosen = random.sample(base_items, item_count)
        items = []
        for name, desc in chosen:
            rarity = pick_rarity()
            items.append({
                "name": name,
                "rarity": rarity,
                "value": item_value(rarity),
                "desc": desc,
            })
        self._items = items


class room_holder:
    def __init__(self):
        self._rows = 3
        self._cols = 4
        self._array_of_rooms = [[None for _ in range(self._cols)] for _ in range(self._rows)]
        self._cur_pos_x = 0
        self._cur_pos_y = 0

    def add_empty_room(self, x_row, y_col):
        print(f"Added empty room at x_row: {x_row}, y_col: {y_col}")
        room = Room()
        room._seed = hash(f"{x_row}_{y_col}")
        self._array_of_rooms[y_col][x_row] = room

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
        if self._rows > cur_y + 1:
            if arr[cur_y + 1][cur_x] != None:
                ret_string += "North "
        if cur_y > 0:
            if arr[cur_y - 1][cur_x] != None:
                ret_string += "South "
        if self._cols > cur_x + 1:
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
        theme_era = all_global_vars.get_player_character(userId).get_theme()
        # Cache the rendered map HTML per room to avoid re-rendering every time
        cur_room = self.get_current_room()
        if not getattr(cur_room, "_map_html", None):
            cur_room._map_html = generate_room_map(self, theme_era)
        ret_string += cur_room._map_html
        ret_string += "<BR>"

        # Add world minimap (visited/unvisited/current)
        try:
            mini_html = self.render_minimap()
            ret_string += f'<div data-role="worldmap">{mini_html}</div>'
            ret_string += "<BR>"
        except Exception:
            pass

        ret_string += self.get_current_room()._description
        ret_string += "<BR>"
        ret_string += self.get_exits()
        items_here = getattr(self.get_current_room(), "_items", []) or []
        if items_here:
            def fmt(it):
                if isinstance(it, dict):
                    return it.get('name', '')
                return str(it)
            ret_string += "<BR>Items here: " + ", ".join([fmt(x) for x in items_here])
        else:
            ret_string += "<BR>Items here: none"
        return ret_string

    def to_dict(self):
        """
        Convert room object to a dictionary for storage into a DB
        """
        rooms = []
        for y in range(self._rows):
            for x in range(self._cols):
                r = self._array_of_rooms[y][x]
                if r is None:
                    continue

                rooms.append({
                    "x": x,
                    "y": y,
                    "visited": bool(getattr(r, "_visited", False)),
                    "description": getattr(r, "_description", None),
                    "items": list(getattr(r, "_items", []) or []),
                    "seed": getattr(r, "_seed", None),
                })

        return {
            "rows": self._rows,
            "cols": self._cols,
            "cur_pos_x": self._cur_pos_x,
            "cur_pos_y": self._cur_pos_y,
            "rooms": rooms,
        }

    @classmethod
    def from_dict(cls, doc):
        """
        Rehydrate room object from dictionary data
        """
        re_room_holder = cls()

        re_room_holder._rows = int(doc.get("rows", 3))
        re_room_holder._cols = int(doc.get("cols", 4))
        re_room_holder._array_of_rooms = [[None for _ in range(re_room_holder._cols)]
                                                for _ in range(re_room_holder._rows)]

        re_room_holder._cur_pos_x = int(doc.get("cur_pos_x", 0))
        re_room_holder._cur_pos_y = int(doc.get("cur_pos_y", 0))

        for room_data in doc.get("rooms", []):
            x = int(room_data["x"])
            y = int(room_data["y"])
            r = Room()
            r._visited = bool(room_data.get("visited", False))
            r._description = room_data.get("description", None)
            r._items = room_data.get("items", []) or []
            r._seed = room_data.get("seed")
            re_room_holder._array_of_rooms[y][x] = r

        return re_room_holder

    def persist_room(self, userId, player_character):
        """
        Update current room array into the DB
        """
        user_doc = user_db.get_user_by_id(userId)
        char_id = user_doc.get("_player_character_id")
        if not char_id:
            return

        player_character.update_char(char_id, {"rooms_visited": self.to_dict()})

    def list_items(self):
        cur = self.get_current_room()
        if cur is None:
            return []
        return list(getattr(cur, "_items", []) or [])

    def pickup_item(self, item_name, player_character):
        cur = self.get_current_room()
        if cur is None:
            return False, "No room found."
        if not getattr(cur, "_items", None):
            return False, "There are no items to pick up here."
        for idx, val in enumerate(cur._items):
            name = val.get("name") if isinstance(val, dict) else str(val)
            if name.lower() == item_name.lower():
                item = cur._items.pop(idx)
                player_character.add_item(item)
                cur._map_html = None  # force redraw without the item
                return True, name
        return False, "That item is not here."

    def drop_item(self, item_name, player_character):
        cur = self.get_current_room()
        if cur is None:
            return False, "No room found."
        removed = player_character.remove_item(item_name)
        if removed is None:
            return False, "You don't have that item."
        cur_items = getattr(cur, "_items", None)
        if cur_items is None:
            cur._items = []
        cur._items.append(removed)
        cur._map_html = None  # force redraw with the dropped item
        name = removed.get("name") if isinstance(removed, dict) else str(removed)
        return True, name

    def describe_npc(self, userId):
        return self.get_current_room()._npc._name + " looks like " + self.get_current_room()._npc._description
    
    def talk_to_npc(self, userId, talk_string):
        return self.get_current_room()._npc.talk(userId, talk_string)
    
    def move_north(self, userId):
        cur_x = self._cur_pos_x
        cur_y = self._cur_pos_y
        arr = self._array_of_rooms

        if self._rows > cur_y + 1:
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

        if self._rows > cur_x + 1:
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
                return '<span style="color:#4da3ff">[E]</span>'
            if getattr(r, "_visited", False):
                return '<span style="color:#66ff66">[-]</span>'
            return '<span style="color:#aaa">[?]</span>'

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
                        row_parts.append('<span style="color:#777">───</span>')
                    else:
                        row_parts.append('   ')
            lines.append(''.join(row_parts))

            # vertical connectors (skip after last printed row)
            if y > 0:
                conn_parts = []
                for x in range(cols):
                    if arr[y][x] is not None and arr[y - 1][x] is not None:
                        conn_parts.append(
                            '  '
                            '<span style="color:#777">│</span>'
                            '  '
                        )
                    else:
                        conn_parts.append('     ')
                    # keep spacing with horizontal gaps too
                    if x < cols - 1:
                        conn_parts.append('   ')
                lines.append(''.join(conn_parts))

        legend = (
            '<div style="margin-top:8px;color:#bbb">'
            '<span style="color:#4da3ff">[E]</span> You   '
            '<span style="color:#66ff66">[-]</span> Visited   '
            '<span style="color:#aaa">[?]</span> Unexplored   '
            '<span style="color:#777">─│</span> Passages'
            '</div>'
        )

        wrapper = (
            '<div style="border:1px solid #333;padding:8px;border-radius:6px;'
            'background:#0b0b0b">'
            + '<pre style="margin:0;line-height:1.2">'
            + "\n".join(lines)
            + '</pre>'
            + legend
            + '</div>'
        )
        return wrapper
