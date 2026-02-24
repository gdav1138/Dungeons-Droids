import random
import user_db
import os
from bson import ObjectId
from open_ai_api import call_ai
from all_global_vars import all_global_vars
from map_generator import generate_room_map
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv('URI'))
db = client["dungeons_droids"]
room_collection = db["rooms"]

class Room:
    def __init__(self, x_cord, y_cord, npc_factory=None):
        self._description = "Not Generated Yet"
        self._visited = False
        self._map_html = None
        self._npc_factory = npc_factory
        self._npc = None
        self._room_pos_x = x_cord
        self._room_pos_y = y_cord
        self._items = []
        self._room_identity = None

    def get_npc(self):
        if self._npc is not None:
            return self._npc

        npc_id = getattr(self, "_npc_id", None)
        if npc_id is None:
            return None

        from humanoid import Npc

        self._npc = Npc.rehydrate_npc(npc_id)
        return self._npc

    def get_id(self):
        return self._id

    def set_id(self, room_id):
        self._id = room_id

    def set_room_pos(self, pos_x, pos_y):
        self._room_pos_x = pos_x
        self._room_pos_y = pos_y

    def generate_description(self, userId, npc=None):
        print("GEN_DESC room id:", getattr(self, "_id", None),
              "pos:", self._room_pos_x, self._room_pos_y,
              "factory:", self._npc_factory)

    def get_npc(self):
        if self._npc is not None:
            return self._npc

        npc_id = getattr(self, "_npc_id", None)
        if npc_id is None:
            return None

        from humanoid import Npc

        self._npc = Npc.rehydrate_npc(npc_id)
        return self._npc

    def get_id(self):
        return self._id

    def set_id(self, room_id):
        self._id = room_id

    def set_room_pos(self, pos_x, pos_y):
        self._room_pos_x = pos_x
        self._room_pos_y = pos_y

    def generate_description(self, userId, npc=None):
        print("GEN_DESC room id:", getattr(self, "_id", None),
              "pos:", self._room_pos_x, self._room_pos_y,
              "factory:", self._npc_factory)

        # Generate NPC for room
        if npc is None:
            if self._npc_factory is None:
                raise RuntimeError("No npc_factory provided and npc is None")
            npc = self._npc_factory(userId)

        self._npc = npc

        # Set room coordinates for NPC
        self._npc.set_room(self._room_pos_x, self._room_pos_y)

        # Store NPC
        npc_id = self._npc.store_npc()
        self._npc_id = npc_id
        self.update_room(self._id, {"_npc_id": npc_id})  # Update room with npc_id

        # Generate Room Description
        client_response = ""
        setup_string = ("Make up a location or MUD room description fitting the theme "
                        + all_global_vars.get_player_character(userId).get_theme()
                        + " for a character named "
                        + all_global_vars.get_player_character(userId).get_name()
                        + ". Don't list any exits or items or anything other than a description of a location.")
        if getattr(self, "_room_identity", None):
            setup_string += (" The room archetype is " + self._room_identity +
                             ". Make this location feel visually distinct from other rooms.")
        if self._npc is not None:
            setup_string += ("Include a mention of an NPC named " + self._npc.get_name() +
                             " and subtlely include the description " + self._npc.get_description())
        client_response += call_ai(setup_string) + "\n"
        self._description = client_response
        self._visited = True

        # Seed deterministic room loot based on position/description
        seed_key = getattr(self, "_seed", None)
        if seed_key is None:
            seed_key = random.randint(1, 999999)
            self._seed = seed_key
        random.seed(seed_key)

        theme_lower = (all_global_vars.get_player_character(userId).get_theme() or "").lower()
        if "cyber" in theme_lower:
            base_items = [
                ("credits chip", "A small encoded chip worth a few credits."),
                ("data shard", "Encrypted storage crystal."),
                ("plasma cell", "Hums faintly with charge."),
                ("medkit", "Sterile wraps and coagulant foam."),
                ("neural jack", "A small cortex interface plug."),
                ("encrypted drive", "Locked storage device, data unknown."),
                ("stim patch", "Adhesive stimulant strip."),
                ("keycard", "A magnetic access card, lightly scratched."),
                ("synth fiber", "A coil of high-tensile synthetic cord."),
                ("micro drone", "A palm-sized recon drone, damaged."),
            ]
        elif "steam" in theme_lower:
            base_items = [
                ("cog token", "A brass token stamped with a gear emblem."),
                ("gear fragment", "Jagged cog from a larger machine."),
                ("metal scrap", "Useful for patchwork repairs."),
                ("oil flask", "Stoppered flask of machine oil."),
                ("sealed vial", "Opaque fluid, cool to touch."),
                ("copper tube", "A short length of pressure-rated piping."),
                ("wrench", "A heavy iron spanner, well-worn."),
                ("pressure gauge", "Cracked glass dial, still functional."),
                ("brass compass", "Engraved compass with a spinning needle."),
                ("steam crystal", "A heat-resonant mineral shard."),
            ]
        else:  # Medieval
            base_items = [
                ("bronze coin", "Ancient coin, its face worn smooth."),
                ("rusty dagger", "A pitted blade with a worn leather grip."),
                ("leather satchel", "A weathered satchel with a broken clasp."),
                ("torch", "Wrapped in pitch-soaked cloth."),
                ("old map", "Faded parchment with partial routes."),
                ("copper key", "Small key etched with runes."),
                ("rations", "Dry but filling travel food."),
                ("rope", "Coiled hemp rope, 30ft."),
                ("gemstone", "Uncut gem catching stray light."),
                ("ancient scroll", "Sealed with brittle wax."),
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

        # Update room with new description and items generated.
        self.update_room(self._id, {
            "description": self._description,
            "visited": True,
            "items": self._items,
            "seed": self._seed
        })

    def store_room(self):
        """
        Stores a room object in the MongoDB and returns the player_character_id.
        """
        # Convert room object to dictionary
        room_doc = {
            "description": self._description,
            "visited": self._visited,
            "map": self._map_html,
            "x": self._room_pos_x,
            "y": self._room_pos_y,
            "items": self._items,
            "identity": self._room_identity,
            "items": self._items
        }

        result = room_collection.insert_one(room_doc)
        print(f"Room stored with character_id: {result.inserted_id}")
        self._id = result.inserted_id
        return self._id

    def update_room(self, room_id, updates):
        """
        Updates a user doc with the given updates.
        """
        query_filter = {"_id": room_id}
        update_operation = {"$set": updates}

        result = room_collection.update_one(query_filter, update_operation)
        print(f"Room {room_id} update result: {result.modified_count} modified")
        return result


class room_holder:
    def __init__(self):
        self._rows = 3
        self._cols = 4
        self._array_of_rooms = [[None for _ in range(self._cols)] for _ in range(self._rows)]
        self._cur_pos_x = 0
        self._cur_pos_y = 0
        self._npc_factory = None

    def configure_grid(self, rows, cols):
        self._rows = max(2, int(rows))
        self._cols = max(2, int(cols))
        self._array_of_rooms = [[None for _ in range(self._cols)] for _ in range(self._rows)]
        self._cur_pos_x = 0
        self._cur_pos_y = 0

    def generate_random_connected_room_coords(self, min_rooms=6, max_rooms=14, start_x=0, start_y=0):
        max_cells = self._rows * self._cols
        min_rooms = max(1, min(int(min_rooms), max_cells))
        max_rooms = max(min_rooms, min(int(max_rooms), max_cells))
        target_rooms = random.randint(min_rooms, max_rooms)
        start_x = max(0, min(int(start_x), self._cols - 1))
        start_y = max(0, min(int(start_y), self._rows - 1))

        coords = {(start_x, start_y)}
        frontier = {(start_x, start_y)}

        while len(coords) < target_rooms and frontier:
            cx, cy = random.choice(tuple(frontier))
            neighbors = [(cx + 1, cy), (cx - 1, cy), (cx, cy + 1), (cx, cy - 1)]
            random.shuffle(neighbors)

            added = False
            for nx, ny in neighbors:
                if nx < 0 or ny < 0 or nx >= self._cols or ny >= self._rows:
                    continue
                if (nx, ny) in coords:
                    continue

                coords.add((nx, ny))
                frontier.add((nx, ny))
                added = True
                if len(coords) >= target_rooms:
                    break

            if not added:
                frontier.discard((cx, cy))

        self._cur_pos_x = start_x
        self._cur_pos_y = start_y
        return list(coords)

    def add_empty_room(self, x_row, y_col, room_identity=None):
        print(f"Added empty room at x_row: {x_row}, y_col: {y_col}")
        room = Room(x_row, y_col, npc_factory=self._npc_factory)
        room._seed = hash(f"{x_row}_{y_col}")
        room._room_identity = room_identity
        self._array_of_rooms[y_col][x_row] = room
        return room.store_room()

    def get_room(self, userId, x, y):
        if x < 0 or x >= self._cols or y < 0 or y >= self._rows:
            return None

        cached_room = self._array_of_rooms[y][x]
        if cached_room is not None:
            if getattr(cached_room, "_npc_factory", None) is None:
                cached_room._npc_factory = getattr(self, "_npc_factory", None)
            return cached_room

        player = all_global_vars.get_player_character(userId)
        room_id = player.get_room_id_at(x,y)

        if y < 0 or y >= self._rows or x < 0 or x >= self._cols:
            return None

        cached_room = self._array_of_rooms[y][x]
        if cached_room is not None:
            if getattr(cached_room, "_npc_factory", None) is None:
                cached_room._npc_factory = getattr(self, "_npc_factory", None)
            return cached_room

        player = all_global_vars.get_player_character(userId)
        room_id = player.get_room_id_at(x,y)

        if room_id is None:
            return None

        mongo_room_id = ObjectId(room_id) if not isinstance(room_id, ObjectId) else room_id

        room_doc = room_collection.find_one({"_id": mongo_room_id})
        if not room_doc:
            return None

        r = Room(x, y, npc_factory=getattr(self, "_npc_factory", None))
        r._id = room_doc["_id"]
        r._visited = bool(room_doc.get("visited", False))
        r._description = room_doc.get("description")
        r._items = room_doc.get("items") or []
        r._seed = room_doc.get("seed")
        r._room_identity = room_doc.get("identity")
        r._npc_id = room_doc.get("_npc_id")
        r._npc = None

        self._array_of_rooms[y][x] = r
        return r

    def get_current_room(self, userId):
        return self.get_room(userId, self._cur_pos_x, self._cur_pos_y)

    def get_current_pos(self):
        return self._cur_pos_x, self._cur_pos_y

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

    def get_full_description(self, userId, npc=None):
        print(f"Getting full desc for {self._cur_pos_x}, {self._cur_pos_y}")

        cur_room = self.get_current_room(userId)
        if cur_room == None:
            return "Error: Tried to describe a None room."
        if cur_room._visited == False:
            cur_room.generate_description(userId)

        ret_string = ""
        theme_era = all_global_vars.get_player_character(userId).get_theme()
        # Cache the rendered map HTML per room to avoid re-rendering every time
        if not getattr(cur_room, "_map_html", None):
            cur_room._map_html = generate_room_map(self, theme_era, userId=userId)
        ret_string += cur_room._map_html
        ret_string += "<BR>"

        # Add world minimap (visited/unvisited/current)
        try:
            mini_html = self.render_minimap(userId)
            ret_string += f'<div data-role="worldmap">{mini_html}</div>'
            ret_string += "<BR>"
        except Exception:
            pass

        ret_string += cur_room._description
        ret_string += "<BR>"
        ret_string += self.get_exits()
        items_here = getattr(cur_room, "_items", []) or []
        if items_here:
            def fmt(it):
                if isinstance(it, dict):
                    return it.get('name', '')
                return str(it)
            ret_string += "<BR>Items here: " + ", ".join([fmt(x) for x in items_here])
        else:
            ret_string += "<BR>Items here: none"
        return ret_string

    def set_npc_factory(self, factory):
        self._npc_factory = factory

        for y in range(self._rows):
            for x in range(self._cols):
                r = self._array_of_rooms[y][x]
                if r is not None:
                    r._npc_factory = factory

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
        re_room_holder._npc_factory = None

        re_room_holder._rows = int(doc.get("rows", 3))
        re_room_holder._cols = int(doc.get("cols", 4))
        re_room_holder._array_of_rooms = [[None for _ in range(re_room_holder._cols)]
                                                for _ in range(re_room_holder._rows)]

        re_room_holder._cur_pos_x = int(doc.get("cur_pos_x", 0))
        re_room_holder._cur_pos_y = int(doc.get("cur_pos_y", 0))

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

    def list_items(self, userId):
        cur = self.get_current_room(userId)
        if cur is None:
            return []
        return list(getattr(cur, "_items", []) or [])

    def pickup_item(self, userId, item_name, player_character):
        cur = self.get_current_room(userId)
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

    def drop_item(self, userId, item_name, player_character):
        cur = self.get_current_room(userId)
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
        room = self.get_current_room(userId)
        if room is None:
            return "No room found."

        npc = room.get_npc()
        if npc is None:
            return "There is no NPC here."

        name = npc.get_name() or "Someone"
        desc = npc.get_description() or "nothing specific."
        return name + " looks like " + desc

    def talk_to_npc(self, userId, talk_string):
        room = self.get_current_room(userId)
        if room is None:
            return "No room found."
        npc = room.get_npc()
        if npc is None:
            return "There is no one here to talk to."
        return npc.talk(userId, talk_string)

    def check_pass_npc(self, userId):
        room = self.get_current_room(userId)
        if not room or room._npc is None:
            return "There is no NPC here."
        return self.get_current_room(userId).get_npc().allow_pass(userId)

    def move_current_room_npc(self, userId, direction=None):
        cur_room = self.get_current_room(userId)
        if cur_room is None:
            return False, "No room found."

        npc = cur_room.get_npc()
        if npc is None:
            return False, "There is no NPC here to move."

        directions = {
            "north": (0, 1),
            "south": (0, -1),
            "east": (1, 0),
            "west": (-1, 0),
        }

        valid_moves = []
        for name, (dx, dy) in directions.items():
            tx = self._cur_pos_x + dx
            ty = self._cur_pos_y + dy
            target = self.get_room(userId, tx, ty)
            if target is None:
                continue
            if target.get_npc() is not None:
                continue
            valid_moves.append((name, tx, ty, target))

        if not valid_moves:
            return False, "No adjacent room is available for that NPC to move into."

        picked = None
        if direction:
            wanted = direction.strip().lower()
            for option in valid_moves:
                if option[0] == wanted:
                    picked = option
                    break
            if picked is None:
                return False, "That direction is not available for NPC movement."
        else:
            picked = random.choice(valid_moves)

        dir_name, new_x, new_y, target_room = picked

        cur_room._npc = None
        cur_room._npc_id = None
        cur_room.update_room(cur_room._id, {"_npc_id": None})

        target_room._npc = npc
        target_room._npc_id = getattr(npc, "_id", None)
        target_room.update_room(target_room._id, {"_npc_id": target_room._npc_id})

        npc.set_room(new_x, new_y)
        if getattr(npc, "_id", None) is not None:
            npc.update_npc(npc._id, {"x_pos": new_x, "y_pos": new_y})

        npc_name = npc.get_name() or "The NPC"
        return True, f"{npc_name} moved {dir_name}."

    def move_north(self, userId):
        cur_x = self._cur_pos_x
        cur_y = self._cur_pos_y

        if self._rows > cur_y + 1:
            next_room = self.get_room(userId, cur_x, cur_y + 1) # Updating room logic to check/generate rooms
            if next_room is None:
                return "Can't move that way!"

            self._cur_pos_y += 1
            return self.get_full_description(userId)

        return "Can't move that way!"

    def move_south(self, userId):
        cur_x = self._cur_pos_x
        cur_y = self._cur_pos_y

        if self._rows > cur_y - 1:
            next_room = self.get_room(userId, cur_x, cur_y - 1)  # Updating room logic to check/generate rooms
            if next_room is None:
                return "Can't move that way!"

            self._cur_pos_y -= 1
            return self.get_full_description(userId)

        return "Can't move that way!"

    def move_east(self, userId):
        """Move player to the east room if available"""
        cur_x = self._cur_pos_x
        cur_y = self._cur_pos_y

        if self._cols > cur_x + 1:
        if self._rows > cur_x + 1:
            next_room = self.get_room(userId, cur_x + 1, cur_y)  # Updating room logic to check/generate rooms
            if next_room is None:
                return "Can't move that way!"

            self._cur_pos_x += 1
            return self.get_full_description(userId)

        return "Can't move that way!"

    def move_west(self, userId):
        """Move player to the west room if available"""
        cur_x = self._cur_pos_x
        cur_y = self._cur_pos_y

        if self._rows > cur_x - 1:
            next_room = self.get_room(userId, cur_x - 1, cur_y)  # Updating room logic to check/generate rooms
            if next_room is None:
                return "Can't move that way!"

            self._cur_pos_x -= 1
            return self.get_full_description(userId)

        return "Can't move that way!"

    def render_minimap(self, userId):
        """Return an HTML snippet with an ASCII-style minimap of rooms.

        Legend:
        - [E] current position (blue)
        - [?] visited room (green)
        - [?] unexplored room (dim)
        Passages (--- and |) connect adjacent rooms.
        Empty space means no room exists at that coordinate.
        """

        player = all_global_vars.get_player_character(userId)
        for entry in player.get_world_map():
            x, y = entry["x"], entry["y"]
            self.get_room(userId, x, y)

        rows = self._rows
        cols = self._cols
        arr = self._array_of_rooms
        cx = self._cur_pos_x
        cy = self._cur_pos_y

        def has_room(x, y):
            if x < 0 or x >= cols or y < 0 or y >= rows:
                return False
            return arr[y][x] is not None

        def cell_html(x, y):
            if not has_room(x, y):
                return '   '
            r = arr[y][x]
            if x == cx and y == cy:
                return '<span style="color:#4da3ff">[E]</span>'
            if getattr(r, '_visited', False):
                return '<span style="color:#66ff66">[?]</span>'
            return '<span style="color:#aaa">[?]</span>'

        lines = []
        # Render north (top) to south (bottom)
        for y in range(rows - 1, -1, -1):
            # Room row with horizontal passages
            row_parts = []
            for x in range(cols):
                row_parts.append(cell_html(x, y))
                if x < cols - 1:
                    if has_room(x, y) and has_room(x + 1, y):
                        row_parts.append('<span style="color:#666">---</span>')
                    else:
                        row_parts.append('   ')
            lines.append(''.join(row_parts))

            # Vertical passage row between this y and y-1
            if y > 0:
                pass_parts = []
                for x in range(cols):
                    if has_room(x, y) and has_room(x, y - 1):
                        pass_parts.append('<span style="color:#666"> | </span>')
                    else:
                        pass_parts.append('   ')
                    if x < cols - 1:
                        pass_parts.append('   ')
                lines.append(''.join(pass_parts))

        legend = (
            '<div style="margin-top:8px;color:#bbb">'
            '<span style="color:#4da3ff">[E]</span> You   '
            '<span style="color:#66ff66">[?]</span> Visited room   '
            '<span style="color:#aaa">[?]</span> Unexplored room'
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
