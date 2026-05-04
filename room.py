import random
import user_db
import os
from item import get_ai_items
from bson import ObjectId
from open_ai_api import call_ai
from all_global_vars import all_global_vars
from map_generator import generate_room_map, _classify_interior
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()
client = MongoClient(os.getenv('URI'))
db = client["dungeons_droids"]
room_collection = db["rooms"]

# Props present in each room type and the actions players can perform on them.
# loot_chance is the probability (0.0-1.0) of finding an item on search/break/open.
# consumed=True means the prop disappears after a destructive action.
_PROP_DEFS = {
    "library": [
        {"name": "bookshelf",     "actions": ["examine", "search", "read"],               "loot_chance": 0.3,  "consumed": False},
        {"name": "reading table", "actions": ["examine", "search", "push"],               "loot_chance": 0.15, "consumed": False},
        {"name": "candle",        "actions": ["examine", "light", "extinguish", "take"],  "loot_chance": 0.0,  "consumed": True},
    ],
    "crypt": [
        {"name": "sarcophagus",   "actions": ["examine", "open", "push"],                 "loot_chance": 0.7,  "consumed": True,  "count": 2},
        {"name": "altar",         "actions": ["examine", "search", "pray", "touch"],      "loot_chance": 0.4,  "consumed": False},
        {"name": "candle",        "actions": ["examine", "light", "extinguish", "take"],  "loot_chance": 0.0,  "consumed": True,  "count": 3},
        {"name": "cobweb",        "actions": ["examine", "clear", "touch"],               "loot_chance": 0.0,  "consumed": True,  "count": 2},
    ],
    "chapel": [
        {"name": "altar",         "actions": ["examine", "pray", "search"],               "loot_chance": 0.35, "consumed": False},
        {"name": "pew",           "actions": ["examine", "sit", "move", "search"],        "loot_chance": 0.1,  "consumed": False, "count": 4},
        {"name": "torch",         "actions": ["examine", "take", "extinguish"],           "loot_chance": 0.0,  "consumed": True,  "count": 2},
        {"name": "cross",         "actions": ["examine", "pray", "touch"],                "loot_chance": 0.0,  "consumed": False},
    ],
    "market": [
        {"name": "market stall",  "actions": ["examine", "search", "browse"],             "loot_chance": 0.45, "consumed": False},
        {"name": "well",          "actions": ["examine", "drink", "search", "throw coin"],"loot_chance": 0.2,  "consumed": False},
    ],
    "boiler": [
        {"name": "boiler",        "actions": ["examine", "vent", "tamper", "touch"],      "loot_chance": 0.2,  "consumed": False},
        {"name": "pipe",          "actions": ["examine", "bang", "unscrew"],              "loot_chance": 0.1,  "consumed": False},
        {"name": "gear wheel",    "actions": ["examine", "turn", "remove"],               "loot_chance": 0.15, "consumed": True},
        {"name": "steam vent",    "actions": ["examine", "block"],                        "loot_chance": 0.0,  "consumed": False},
    ],
    "tavern": [
        {"name": "bar counter",   "actions": ["examine", "search", "lean on"],            "loot_chance": 0.25, "consumed": False},
        {"name": "table",         "actions": ["examine", "search", "move"],               "loot_chance": 0.15, "consumed": False, "count": 2},
        {"name": "chair",         "actions": ["examine", "sit", "throw", "move"],         "loot_chance": 0.0,  "consumed": False, "count": 3},
        {"name": "barrel",        "actions": ["examine", "break", "search", "drink from"],"loot_chance": 0.4,  "consumed": True,  "count": 3},
        {"name": "mug",           "actions": ["examine", "drink", "throw"],               "loot_chance": 0.0,  "consumed": True,  "count": 2},
    ],
    "throne": [
        {"name": "throne",        "actions": ["examine", "sit", "search"],                "loot_chance": 0.3,  "consumed": False},
        {"name": "pillar",        "actions": ["examine", "touch", "push"],                "loot_chance": 0.0,  "consumed": False},
        {"name": "carpet",        "actions": ["examine", "search", "pull"],               "loot_chance": 0.2,  "consumed": False},
    ],
    "prison": [
        {"name": "cell bars",     "actions": ["examine", "pull", "bend"],                 "loot_chance": 0.0,  "consumed": False},
        {"name": "chains",        "actions": ["examine", "pull", "grab", "take"],         "loot_chance": 0.0,  "consumed": True},
        {"name": "straw pile",    "actions": ["examine", "search", "hide in"],            "loot_chance": 0.35, "consumed": False},
    ],
    "laboratory": [
        {"name": "workbench",     "actions": ["examine", "search", "use"],                "loot_chance": 0.4,  "consumed": False},
        {"name": "flask",         "actions": ["examine", "drink", "throw"],               "loot_chance": 0.0,  "consumed": True},
        {"name": "shelf",         "actions": ["examine", "search"],                       "loot_chance": 0.35, "consumed": False},
        {"name": "alchemy circle","actions": ["examine", "touch", "stand in"],            "loot_chance": 0.0,  "consumed": False},
    ],
    "armory": [
        {"name": "weapon rack",   "actions": ["examine", "search", "take from"],          "loot_chance": 0.5,  "consumed": False},
        {"name": "armor stand",   "actions": ["examine", "search", "use"],                "loot_chance": 0.35, "consumed": False},
        {"name": "shield",        "actions": ["examine", "take", "use"],                  "loot_chance": 0.0,  "consumed": True},
    ],
    "server": [
        {"name": "server rack",   "actions": ["examine", "hack", "search", "unplug"],     "loot_chance": 0.45, "consumed": False},
        {"name": "terminal",      "actions": ["examine", "hack", "use"],                  "loot_chance": 0.4,  "consumed": False},
        {"name": "cable channel", "actions": ["examine", "cut", "pull"],                  "loot_chance": 0.15, "consumed": False},
    ],
    "treasury": [
        {"name": "vault door",    "actions": ["examine", "open", "hack", "touch"],        "loot_chance": 0.0,  "consumed": False},
        {"name": "chest",         "actions": ["examine", "open", "search", "break"],      "loot_chance": 0.85, "consumed": True},
        {"name": "coin pile",     "actions": ["examine", "take from", "scatter"],         "loot_chance": 0.6,  "consumed": True},
    ],
    "generic": [
        {"name": "barrel",        "actions": ["examine", "break", "search", "move"],      "loot_chance": 0.4,  "consumed": True,  "count": 3},
        {"name": "crate",         "actions": ["examine", "break", "search", "move"],      "loot_chance": 0.4,  "consumed": True,  "count": 2},
        {"name": "table",         "actions": ["examine", "search", "move"],               "loot_chance": 0.15, "consumed": False},
        {"name": "torch",         "actions": ["examine", "take", "extinguish"],           "loot_chance": 0.0,  "consumed": True,  "count": 2},
        {"name": "chest",         "actions": ["examine", "open", "search"],               "loot_chance": 0.6,  "consumed": True},
    ],
}

# Extra actions available on specific inventory/room items beyond the universal "examine".
_ITEM_EXTRA_ACTIONS = {
    "torch":           ["light", "use", "extinguish"],
    "rations":         ["eat"],
    "ancient scroll":  ["read", "open"],
    "old map":         ["read", "study"],
    "sealed vial":     ["open", "drink"],
    "oil flask":       ["use", "drink", "pour"],
    "rope":            ["use", "throw"],
    "rusty dagger":    ["use"],
    "copper key":      ["use"],
    "leather satchel": ["open", "search"],
    "gemstone":        ["appraise"],
    "bronze coin":     ["flip"],
    "medkit":          ["use"],
    "stim patch":      ["use", "apply"],
    "data shard":      ["read", "hack", "use"],
    "encrypted drive": ["read", "hack", "use"],
    "neural jack":     ["use"],
    "plasma cell":     ["use"],
    "keycard":         ["use"],
    "micro drone":     ["use", "launch"],
    "synth fiber":     ["use", "throw"],
    "wrench":          ["use"],
    "brass compass":   ["use", "read"],
    "steam crystal":   ["use"],
    "pressure gauge":  ["read", "use"],
    "cog token":       ["flip"],
    "gear fragment":   ["use"],
    "metal scrap":     ["use"],
    "copper tube":     ["use"],
    "credits chip":    ["use"],
}


def _remove_obj(cur_room, player_char, obj_src, obj_name):
    """Remove an object from its source (room items or player inventory)."""
    if obj_src == "room_item":
        cur_room._items = [
            i for i in cur_room._items
            if (i.get("name") if isinstance(i, dict) else i) != obj_name
        ]
    elif obj_src == "inventory":
        player_char.remove_item(obj_name)


def _remove_one_prop(props, name):
    """Remove only the first matching prop, leaving any duplicates intact."""
    result, removed = [], False
    for p in props:
        if not removed and p["name"] == name:
            removed = True
        else:
            result.append(p)
    return result


def _generate_loot_item(theme):
    """Generate a random loot item appropriate for the given theme."""
    theme_lower = (theme or "").lower()
    if "cyber" in theme_lower:
        pool = [
            ("credits chip", "A small encoded chip worth a few credits."),
            ("data shard", "Encrypted storage crystal."),
            ("plasma cell", "Hums faintly with charge."),
            ("stim patch", "Adhesive stimulant strip."),
            ("medkit", "Sterile wraps and coagulant foam."),
        ]
    elif "steam" in theme_lower:
        pool = [
            ("cog token", "A brass token stamped with a gear emblem."),
            ("gear fragment", "Jagged cog from a larger machine."),
            ("sealed vial", "Opaque fluid, cool to touch."),
            ("steam crystal", "A heat-resonant mineral shard."),
            ("metal scrap", "Useful for patchwork repairs."),
        ]
    else:
        pool = [
            ("bronze coin", "Ancient coin, its face worn smooth."),
            ("rations", "Dry but filling travel food."),
            ("rusty dagger", "A pitted blade with a worn leather grip."),
            ("old map", "Faded parchment with partial routes."),
            ("torch", "Wrapped in pitch-soaked cloth."),
        ]
    name, desc = random.choice(pool)
    rarity_table = [("Common", 0.6), ("Uncommon", 0.25), ("Rare", 0.12), ("Epic", 0.03)]
    roll, acc, rarity = random.random(), 0.0, "Common"
    for r, p in rarity_table:
        acc += p
        if roll <= acc:
            rarity = r
            break
    value = random.randint(*{"Common": (1, 8), "Uncommon": (10, 30), "Rare": (40, 120), "Epic": (150, 400)}.get(rarity, (1, 8)))
    return {"name": name, "desc": desc, "rarity": rarity, "value": value}


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
        self._props = []
        self._interior_type = None
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

        # Get a list of items
        items = get_ai_items(theme_lower, self._description, self._room_identity, random)
        self._items = items

        # Update room with new description and items generated.
        self.update_room(self._id, {
            "description": self._description,
            "visited": True,
            "items": self._items,
            "seed": self._seed,
            "props": self._props,
            "interior_type": self._interior_type,
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
            "props": self._props,
            "interior_type": self._interior_type,
            "identity": self._room_identity,
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
        r._props = room_doc.get("props") or []
        r._interior_type = room_doc.get("interior_type")
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
                return it.get("name", "") if isinstance(it, dict) else str(it)
            ret_string += "<BR>Items here: " + ", ".join([fmt(x) for x in items_here])
        else:
            ret_string += "<BR>Items here: none"

        props_here = getattr(cur_room, "_props", []) or []
        if props_here:
            counts = {}
            for p in props_here:
                counts[p["name"]] = counts.get(p["name"], 0) + 1
            prop_strs = [f"{n} ×{c}" if c > 1 else n for n, c in counts.items()]
            ret_string += "<BR>You can interact with: " + ", ".join(prop_strs)

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
                try:
                    # Inform quest system that an item was obtained (for obtain-item quests).
                    player_character.record_item_obtained(item)
                except AttributeError:
                    pass
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

    def fight_npc(self, userId, action="attack"):
        room = self.get_current_room(userId)
        if not room or room._npc is None:
            return "There is no NPC here"
        return room.get_npc().fight(userId, action=action)

    def bribe_npc(self, userId, gold_amount):
        room = self.get_current_room(userId)
        if not room or room._npc is None:
            return "There is no NPC here to bribe."
        return room.get_npc().bribe(userId, gold_amount)

    def bribe_npc_item(self, userId, item_name):
        room = self.get_current_room(userId)
        if not room or room._npc is None:
            return "There is no NPC here to bribe."
        return room.get_npc().bribe_with_item(userId, item_name)

    def interact_environment(self, userId, action, target):
        cur_room = self.get_current_room(userId)
        if cur_room is None:
            return "No room found."

        player_char = all_global_vars.get_player_character(userId)
        theme = player_char.get_theme() or "Medieval"
        target_lower = target.lower().strip()

        # Search props, then room items, then player inventory.
        matched_prop = next(
            (p for p in (getattr(cur_room, "_props", []) or [])
             if target_lower in p["name"].lower() or p["name"].lower() in target_lower),
            None,
        )
        matched_room_item = None
        if not matched_prop:
            matched_room_item = next(
                (i for i in (getattr(cur_room, "_items", []) or [])
                 if target_lower in (i.get("name", "") if isinstance(i, dict) else str(i)).lower()),
                None,
            )
        matched_inv_item = None
        if not matched_prop and not matched_room_item:
            matched_inv_item = next(
                (i for i in player_char.get_inventory()
                 if target_lower in (i.get("name", "") if isinstance(i, dict) else str(i)).lower()),
                None,
            )

        if not matched_prop and not matched_room_item and not matched_inv_item:
            return f"You don't see any '{target}' here to {action}."

        # Build object info
        if matched_prop:
            obj_name = matched_prop["name"]
            obj_desc = f"a {obj_name} in the room"
            valid_actions = matched_prop.get("actions", ["examine"])
            loot_chance = matched_prop.get("loot_chance", 0.0)
            consumed = matched_prop.get("consumed", False)
            obj_src = "prop"
        elif matched_room_item:
            obj = matched_room_item
            obj_name = obj.get("name", target) if isinstance(obj, dict) else str(obj)
            obj_desc = obj.get("desc", f"a {obj_name}") if isinstance(obj, dict) else f"a {obj_name}"
            valid_actions = ["examine"] + _ITEM_EXTRA_ACTIONS.get(obj_name.lower(), [])
            loot_chance, consumed = 0.0, False
            obj_src = "room_item"
        else:
            obj = matched_inv_item
            obj_name = obj.get("name", target) if isinstance(obj, dict) else str(obj)
            obj_desc = obj.get("desc", f"a {obj_name}") if isinstance(obj, dict) else f"a {obj_name}"
            valid_actions = ["examine"] + _ITEM_EXTRA_ACTIONS.get(obj_name.lower(), [])
            loot_chance, consumed = 0.0, False
            obj_src = "inventory"

        # "examine" always works on anything found.
        if action not in valid_actions and action != "examine":
            return (f"You can't {action} the {obj_name}.<BR>"
                    f"You can: {', '.join(valid_actions)}.")

        # ── Mechanical effects ────────────────────────────────────────────────
        effect_text = ""
        loot_found = None
        modified = False

        # Eating / drinking consumables
        if action == "eat" and obj_src in ("room_item", "inventory"):
            heal = 10
            player_char._health = min(100, player_char._health + heal)
            _remove_obj(cur_room, player_char, obj_src, obj_name)
            effect_text = f"+{heal} HP"
            modified = True

        elif action == "drink" and obj_src in ("room_item", "inventory", "prop"):
            if random.random() < 0.7:
                heal = random.randint(8, 20)
                player_char._health = min(100, player_char._health + heal)
                effect_text = f"+{heal} HP"
            else:
                dmg = random.randint(5, 15)
                player_char._health = max(1, player_char._health - dmg)
                effect_text = f"-{dmg} HP (tasted awful)"
            if obj_src != "prop":
                _remove_obj(cur_room, player_char, obj_src, obj_name)
            modified = True

        elif action == "use" and "medkit" in obj_name.lower():
            heal = 25
            player_char._health = min(100, player_char._health + heal)
            _remove_obj(cur_room, player_char, obj_src, obj_name)
            effect_text = f"+{heal} HP"
            modified = True

        elif action in ("use", "apply") and "stim" in obj_name.lower():
            heal = 15
            player_char._health = min(100, player_char._health + heal)
            _remove_obj(cur_room, player_char, obj_src, obj_name)
            effect_text = f"+{heal} HP"
            modified = True

        # Loot-generating actions on props
        elif obj_src == "prop" and action in ("break", "smash", "open", "search", "loot",
                                               "hack", "take from", "rummage through",
                                               "rummage in", "browse"):
            if loot_chance > 0 and random.random() < loot_chance:
                loot_found = _generate_loot_item(theme)
                cur_room._items.append(loot_found)
                effect_text = f"You find a {loot_found['name']} ({loot_found['rarity']})!"
            else:
                effect_text = "Nothing of value here."
            if consumed or action in ("break", "smash", "open"):
                cur_room._props = _remove_one_prop(cur_room._props, obj_name)
            modified = True

        # Taking a prop (torch, chain, shield…)
        elif obj_src == "prop" and action == "take":
            item = {"name": obj_name, "desc": obj_desc, "rarity": "Common", "value": 1}
            player_char.add_item(item)
            cur_room._props = _remove_one_prop(cur_room._props, obj_name)
            effect_text = f"{obj_name} added to inventory."
            modified = True

        # Persist if state changed
        if modified:
            self.persist_room(userId, player_char)
            user_doc = user_db.get_user_by_id(userId)
            char_id = user_doc.get("_player_character_id") if user_doc else None
            if char_id:
                player_char.update_player_character(char_id)
                cur_room_doc_id = getattr(cur_room, "_id", None)
                if cur_room_doc_id:
                    cur_room.update_room(cur_room_doc_id, {
                        "items": list(getattr(cur_room, "_items", [])),
                        "props": list(getattr(cur_room, "_props", [])),
                    })

        # ── AI narration ─────────────────────────────────────────────────────
        room_snippet = (cur_room._description or "")[:300]
        npc = cur_room.get_npc()
        npc_note = f" An NPC named {npc.get_name()} is present." if npc else ""
        result_note = effect_text if effect_text else "No special result — describe the sensory experience."

        prompt = (
            f"Theme: {theme}. Room: {room_snippet}{npc_note}\n"
            f"The player performs '{action}' on the {obj_name} ({obj_desc}).\n"
            f"Result: {result_note}\n"
            f"Write 2-3 sentences narrating this in an immersive, theme-appropriate way. "
            f"Weave the result naturally into the description. No lists, no headings."
        )
        narrative = call_ai(prompt)

        if effect_text:
            return f"{narrative}<BR><em>({effect_text})</em>"
        return narrative

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

        if cur_x > 0:
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
