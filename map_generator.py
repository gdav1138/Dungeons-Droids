import io
import base64
import random
from PIL import Image, ImageDraw
from ai_layout import get_map_layout


def generate_room_map(room_holder, theme_era="Medieval"):
    """Generate a detailed top-down D&D style battle map"""
    width = 900
    height = 675
    img = Image.new('RGB', (width, height), color='#0d0d0d')
    draw = ImageDraw.Draw(img)
    
    # Get current room info
    cur_x = room_holder._cur_pos_x
    cur_y = room_holder._cur_pos_y
    room_array = room_holder._array_of_rooms
    current_room = room_array[cur_y][cur_x]
    description = current_room._description.lower() if current_room._description else ""
    
    # Set theme colors (defaults; AI layout may override floor colors)
    theme_lower = theme_era.lower().strip()
    print(f"DEBUG: Theme era = '{theme_era}', theme_lower = '{theme_lower}'")
    if 'cyber' in theme_lower or 'sci' in theme_lower or 'punk' in theme_lower and 'steam' not in theme_lower:
        print("DEBUG: Using cyberpunk colors")
        floor_base = '#1a2a3a'
        floor_accent = '#0d1a25'
        wall_base = '#0a1520'
        wall_accent = '#152535'
        furniture_color = '#2a4a5a'
    elif 'steam' in theme_lower or 'cog' in theme_lower:
        print("DEBUG: Using steampunk colors")
        floor_base = '#4a3a2a'
        floor_accent = '#3a2a1a'
        wall_base = '#2a1a0a'
        wall_accent = '#4a2a1a'
        furniture_color = '#6a4a3a'
    elif 'west' in theme_lower or 'cowboy' in theme_lower or 'saloon' in theme_lower:
        print("DEBUG: Using western colors")
        floor_base = '#8b7355'
        floor_accent = '#6b5345'
        wall_base = '#5a4a3a'
        wall_accent = '#7a6a5a'
        furniture_color = '#a89070'
    elif 'horror' in theme_lower or 'dark' in theme_lower or 'gothic' in theme_lower:
        print("DEBUG: Using horror colors")
        floor_base = '#1a1a1a'
        floor_accent = '#0a0a0a'
        wall_base = '#2a1a1a'
        wall_accent = '#4a2a2a'
        furniture_color = '#3a2a2a'
    elif 'dystop' in theme_lower or 'post' in theme_lower:
        print("DEBUG: Using dystopian colors")
        floor_base = '#2a3a3a'
        floor_accent = '#1a2a2a'
        wall_base = '#1a1a2a'
        wall_accent = '#2a2a4a'
        furniture_color = '#3a3a5a'
    else:  # Medieval (default)
        print("DEBUG: Using medieval colors (default)")
        floor_base = '#5a4a3a'
        floor_accent = '#4a3a2a'
        wall_base = '#2a2520'
        wall_accent = '#3a3530'
        furniture_color = '#6a5545'
    
    # Seed for consistent generation per room
    random.seed(hash(f"{cur_x}_{cur_y}"))
    
    # Grid settings for tile-based drawing
    tile_size = 30
    margin = 75
    room_width = width - 2 * margin
    room_height = height - 2 * margin
    
    # Build exits map for AI
    cols = room_holder._cols
    rows = room_holder._rows
    exits_map = {
        'north': bool(cur_y + 1 < rows and room_array[cur_y + 1][cur_x] is not None),
        'south': bool(cur_y > 0 and room_array[cur_y - 1][cur_x] is not None),
        'east': bool(cur_x + 1 < cols and room_array[cur_y][cur_x + 1] is not None),
        'west': bool(cur_x > 0 and room_array[cur_y][cur_x - 1] is not None),
    }

    # Fast path: avoid network calls for layout to reduce latency
    use_ai_layout = False  # set True to let the AI suggest colors/props
    if use_ai_layout:
        layout = get_map_layout(description, theme_era, exits_map)
    else:
        # Most rooms are chambers (rectangular with occasional subtle alcoves)
        room_types = ["chamber", "chamber", "chamber", "chamber"]
        layout = {"room_type": random.choice(room_types), "floor": {}}

    # Allow AI to override floor colors
    try:
        floor_base = layout.get('floor', {}).get('base', floor_base)
        floor_accent = layout.get('floor', {}).get('accent', floor_accent)
    except Exception:
        pass

    room_type = (layout.get('room_type') or '').lower()
    has_alley = room_type == 'alley'
    has_corridor = room_type == 'corridor'
    has_tavern = room_type == 'tavern'
    has_library = room_type == 'library'

    # Configuration: keep rooms clean (no random props) unless toggled
    draw_furniture = False  # set True to re-enable props/furniture rendering

    # Room mask helper
    def create_room_mask(tiles_x, tiles_y, room_type):
        m = [[False for _ in range(tiles_x)] for _ in range(tiles_y)]

        def fill_rect(x1, y1, x2, y2):
            for yy in range(y1, y2):
                for xx in range(x1, x2):
                    if 0 <= xx < tiles_x and 0 <= yy < tiles_y:
                        m[yy][xx] = True

        # Different room shapes and sizes
        shape_choices = ["rect", "wide", "tall", "square"]
        shape = random.choice(shape_choices)

        w = max(3, tiles_x - 2)
        h = max(3, tiles_y - 2)

        if shape == "rect":
            # Standard room
            fill_rect((tiles_x - w)//2, (tiles_y - h)//2, (tiles_x + w)//2, (tiles_y + h)//2)
        
        elif shape == "wide":
            # Wide rectangular room - use more width, less height
            w = tiles_x - 1
            h = max(4, tiles_y - 5)
            fill_rect(0, (tiles_y - h)//2, tiles_x, (tiles_y + h)//2)
        
        elif shape == "tall":
            # Tall rectangular room - use more height, less width
            w = max(4, tiles_x - 5)
            h = tiles_y - 1
            fill_rect((tiles_x - w)//2, 0, (tiles_x + w)//2, tiles_y)
        
        elif shape == "square":
            # More square-shaped room
            side = min(w, h)
            fill_rect((tiles_x - side)//2, (tiles_y - side)//2, (tiles_x + side)//2, (tiles_y + side)//2)
        
        else:
            fill_rect((tiles_x - w)//2, (tiles_y - h)//2, (tiles_x + w)//2, (tiles_y + h)//2)

        return m

    # Determine room shape mask (walkable tiles) now that room_type is known
    tiles_x = room_width // tile_size
    tiles_y = room_height // tile_size
    mask = create_room_mask(tiles_x, tiles_y, room_type)

    # Draw floor with detailed tiles using mask
    for gy, y in enumerate(range(margin, height - margin, tile_size)):
        if gy >= tiles_y: break
        for gx, x in enumerate(range(margin, width - margin, tile_size)):
            if gx >= tiles_x: break
            if not mask[gy][gx]:
                continue
            # Add variation
            shade = random.randint(-12, 12)
            r = min(255, max(0, int(floor_base[1:3], 16) + shade))
            g = min(255, max(0, int(floor_base[3:5], 16) + shade))
            b = min(255, max(0, int(floor_base[5:7], 16) + shade))
            color = f'#{r:02x}{g:02x}{b:02x}'
            
            # Draw tile
            draw.rectangle([x, y, x + tile_size - 1, y + tile_size - 1],
                          fill=color, outline=floor_accent, width=1)
            
            # Add subtle corner shadows for depth
            shadow_size = 4
            for i in range(shadow_size):
                darkness = int(shade - (shadow_size - i) * 5)
                sr = max(0, r + darkness)
                sg = max(0, g + darkness)
                sb = max(0, b + darkness)
                shadow_color = f'#{sr:02x}{sg:02x}{sb:02x}'
                draw.line([x + tile_size - shadow_size + i, y + tile_size - 1,
                          x + tile_size - 1, y + tile_size - 1], fill=shadow_color)
                draw.line([x + tile_size - 1, y + tile_size - shadow_size + i,
                          x + tile_size - 1, y + tile_size - 1], fill=shadow_color)
            
            # Optional: accent tiles are disabled to reduce visual clutter
            # If desired, set probability and uncomment below
            # if random.random() > 0.98:
            #     accent_size = tile_size // 2
            #     ax = x + (tile_size - accent_size) // 2
            #     ay = y + (tile_size - accent_size) // 2
            #     draw.rectangle([ax, ay, ax + accent_size, ay + accent_size],
            #                   fill=floor_accent)
    
    # Exits from prepared map
    has_north = exits_map['north']
    has_south = exits_map['south']
    has_east = exits_map['east']
    has_west = exits_map['west']
    
    # Derive a bounding box from the mask for wall placement
    bx_min = tiles_x
    bx_max = 0
    by_min = tiles_y
    by_max = 0
    for y in range(tiles_y):
        for x in range(tiles_x):
            if mask[y][x]:
                bx_min = min(bx_min, x)
                bx_max = max(bx_max, x)
                by_min = min(by_min, y)
                by_max = max(by_max, y)
    if bx_min > bx_max or by_min > by_max:
        bx_min, by_min, bx_max, by_max = 0, 0, tiles_x - 1, tiles_y - 1

    # Convert to pixel coords
    wall_thickness = 38
    wx1 = margin + bx_min * tile_size
    wy1 = margin + by_min * tile_size
    wx2 = margin + (bx_max + 1) * tile_size
    wy2 = margin + (by_max + 1) * tile_size

    # Draw outer walls on mask bounds with exits
    if not has_north:
        draw_stone_wall(draw, wx1, wy1, wx2, wy1 + wall_thickness, wall_base, wall_accent)
    else:
        door_width = 80
        door_x = (wx1 + wx2) // 2 - door_width // 2
        draw_stone_wall(draw, wx1, wy1, door_x - 10, wy1 + wall_thickness, wall_base, wall_accent)
        draw_stone_wall(draw, door_x + door_width + 10, wy1, wx2, wy1 + wall_thickness, wall_base, wall_accent)
        draw_door(draw, door_x, wy1, door_width, wall_thickness, 'north', furniture_color)

    if not has_south:
        draw_stone_wall(draw, wx1, wy2 - wall_thickness, wx2, wy2, wall_base, wall_accent)
    else:
        door_width = 80
        door_x = (wx1 + wx2) // 2 - door_width // 2
        draw_stone_wall(draw, wx1, wy2 - wall_thickness, door_x - 10, wy2, wall_base, wall_accent)
        draw_stone_wall(draw, door_x + door_width + 10, wy2 - wall_thickness, wx2, wy2, wall_base, wall_accent)
        draw_door(draw, door_x, wy2 - wall_thickness, door_width, wall_thickness, 'south', furniture_color)

    if not has_west:
        draw_stone_wall(draw, wx1, wy1, wx1 + wall_thickness, wy2, wall_base, wall_accent)
    else:
        door_height = 80
        door_y = (wy1 + wy2) // 2 - door_height // 2
        draw_stone_wall(draw, wx1, wy1, wx1 + wall_thickness, door_y - 10, wall_base, wall_accent)
        draw_stone_wall(draw, wx1, door_y + door_height + 10, wx1 + wall_thickness, wy2, wall_base, wall_accent)
        draw_door(draw, wx1, door_y, wall_thickness, door_height, 'west', furniture_color)

    if not has_east:
        draw_stone_wall(draw, wx2 - wall_thickness, wy1, wx2, wy2, wall_base, wall_accent)
    else:
        door_height = 80
        door_y = (wy1 + wy2) // 2 - door_height // 2
        draw_stone_wall(draw, wx2 - wall_thickness, wy1, wx2, door_y - 10, wall_base, wall_accent)
        draw_stone_wall(draw, wx2 - wall_thickness, door_y + door_height + 10, wx2, wy2, wall_base, wall_accent)
        draw_door(draw, wx2 - wall_thickness, door_y, wall_thickness, door_height, 'east', furniture_color)

    # If AI provided props, draw them; otherwise fallback to heuristic furniture
    if draw_furniture:
        props = layout.get('props') or []
        if props:
            for p in props:
                _draw_prop(draw, p, margin, width, height, furniture_color, theme_lower)
        else:
            add_room_furniture(draw, description, margin, width, height, furniture_color, theme_lower)
    
    # Draw items in the room
    if hasattr(current_room, '_items') and current_room._items:
        item_positions = []
        num_items = len(current_room._items)
        
        # Generate random positions for items that don't overlap with player center
        for i in range(num_items):
            attempts = 0
            while attempts < 10:
                # Random position within the room bounds, avoiding center
                ix = wx1 + 60 + random.randint(0, (wx2 - wx1 - 120))
                iy = wy1 + 60 + random.randint(0, (wy2 - wy1 - 120))
                
                # Check if far enough from center
                center_x = (wx1 + wx2) // 2
                center_y = (wy1 + wy2) // 2
                dist = ((ix - center_x)**2 + (iy - center_y)**2)**0.5
                
                if dist > 50:  # At least 50 pixels from center
                    item_positions.append((ix, iy))
                    break
                attempts += 1
        
        # Draw items
        for i, item in enumerate(current_room._items):
            if i < len(item_positions):
                ix, iy = item_positions[i]
                item_type = item.get_type()
                
                # Draw different shapes/colors based on item type
                if item_type == 'weapon':
                    # Draw a sword-like shape
                    draw.polygon([(ix, iy - 15), (ix - 4, iy + 10), (ix + 4, iy + 10)],
                               fill='#c0c0c0', outline='#808080')
                    draw.rectangle([ix - 2, iy + 10, ix + 2, iy + 15],
                                 fill='#8b4513', outline='#654321')
                elif item_type == 'armor':
                    # Draw a shield shape
                    draw.polygon([(ix, iy - 12), (ix - 10, iy), (ix - 8, iy + 10), 
                                 (ix + 8, iy + 10), (ix + 10, iy)],
                               fill='#708090', outline='#404040')
                elif item_type == 'potion':
                    # Draw a bottle shape
                    draw.ellipse([ix - 6, iy - 10, ix + 6, iy + 10],
                               fill='#ff0066', outline='#990033')
                    draw.rectangle([ix - 3, iy - 12, ix + 3, iy - 10],
                                 fill='#8b4513', outline='#654321')
                elif item_type == 'treasure':
                    # Draw a chest/gem shape
                    draw.ellipse([ix - 8, iy - 8, ix + 8, iy + 8],
                               fill='#ffd700', outline='#ffaa00')
                else:
                    # Generic item - simple box
                    draw.rectangle([ix - 8, iy - 8, ix + 8, iy + 8],
                                 fill='#90ee90', outline='#228b22')
                
                # Add a subtle glow/highlight
                draw.ellipse([ix - 12, iy - 12, ix + 12, iy + 12],
                           outline='#ffff00', width=1)
    
    # Draw player marker
    player_x = (wx1 + wx2) // 2
    player_y = (wy1 + wy2) // 2
    draw.ellipse([player_x - 12, player_y - 12, player_x + 12, player_y + 12],
                fill='#ff3333', outline='#ffffff', width=3)
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f'<img src="data:image/png;base64,{img_str}"/>'


def _draw_prop(draw, prop, margin, width, height, color, theme):
    """Render a single prop described in normalized coordinates."""
    try:
        px = margin + int(prop.get('x', 0.5) * (width - 2 * margin))
        py = margin + int(prop.get('y', 0.5) * (height - 2 * margin))
        pw = max(12, int(prop.get('w', 0.08) * (width - 2 * margin)))
        ph = max(12, int(prop.get('h', 0.06) * (height - 2 * margin)))
        t = (prop.get('type') or '').lower()
    except Exception:
        return

    x1 = px - pw // 2
    y1 = py - ph // 2
    x2 = px + pw // 2
    y2 = py + ph // 2

    # Simple visuals per prop type
    if t in ('table', 'desk', 'altar', 'console', 'panel'):
        draw.rectangle([x1, y1, x2, y2], fill=color, outline='#3a3a3a', width=2)
    elif t in ('crate', 'box'):
        draw.rectangle([x1, y1, x2, y2], fill=color, outline='#000000', width=2)
        draw.line([x1, y1, x2, y2], fill='#000000', width=1)
        draw.line([x1, y2, x2, y1], fill='#000000', width=1)
    elif t in ('barrel'):
        draw.ellipse([x1, y1, x2, y2], fill=color, outline='#3a3a3a', width=2)
    elif t in ('bookcase', 'shelf'):
        draw.rectangle([x1, y1, x2, y2], fill=color, outline='#3a3a3a', width=2)
        # shelves lines
        for i in range(1, 3):
            y = y1 + i * (ph // 3)
            draw.line([x1+3, y, x2-3, y], fill='#2a2a2a', width=1)
    elif t in ('server', 'mainframe'):
        draw.rectangle([x1, y1, x2, y2], fill='#1a1a1a', outline='#00ffcc', width=2)
        for i in range(3):
            lx = x1 + 6
            ly = y1 + 6 + i * (ph // 3)
            draw.ellipse([lx, ly, lx + 6, ly + 6], fill='#00ffcc')
    elif t in ('boiler', 'gear', 'pipe'):
        draw.ellipse([x1, y1, x2, y2], fill=color, outline='#3a3a3a', width=2)
    else:
        # generic prop
        draw.rectangle([x1, y1, x2, y2], fill=color, outline='#3a3a3a', width=1)


def draw_stone_wall(draw, x1, y1, x2, y2, base_color, accent_color):
    """Draw a textured stone wall with shadows"""
    # Add drop shadow first (slightly offset)
    shadow_offset = 3
    shadow_color = '#000000'
    if x2 - x1 > y2 - y1:  # Horizontal wall
        # Shadow below wall
        for i in range(shadow_offset):
            alpha_factor = (shadow_offset - i) / shadow_offset
            draw.line([x1, y2 + i, x2, y2 + i], fill=shadow_color, width=1)
    else:  # Vertical wall
        # Shadow to the right of wall
        for i in range(shadow_offset):
            alpha_factor = (shadow_offset - i) / shadow_offset
            draw.line([x2 + i, y1, x2 + i, y2], fill=shadow_color, width=1)
    
    # Main wall
    draw.rectangle([x1, y1, x2, y2], fill=base_color, outline=accent_color, width=2)
    
    # Add stone texture
    for i in range(int((x2 - x1) / 40)):
        for j in range(int((y2 - y1) / 40)):
            sx = x1 + i * 40 + random.randint(-5, 5)
            sy = y1 + j * 40 + random.randint(-5, 5)
            draw.rectangle([sx, sy, sx + 35, sy + 35],
                          outline=accent_color, width=1)


def draw_door(draw, x, y, w, h, direction, color):
    """Draw a door"""
    if direction in ['north', 'south']:
        # Horizontal door
        draw.rectangle([x + 10, y, x + w - 10, y + h],
                      fill=color, outline='#3a3a3a', width=2)
        # Door handle
        handle_x = x + w // 2
        handle_y = y + h // 2
        draw.ellipse([handle_x - 4, handle_y - 4, handle_x + 4, handle_y + 4],
                    fill='#ccaa66')
    else:
        # Vertical door
        draw.rectangle([x, y + 10, x + w, y + h - 10],
                      fill=color, outline='#3a3a3a', width=2)
        handle_x = x + w // 2
        handle_y = y + h // 2
        draw.ellipse([handle_x - 4, handle_y - 4, handle_x + 4, handle_y + 4],
                    fill='#ccaa66')


def add_tavern_furniture(draw, margin, width, height, color):
    """Add tavern-style furniture"""
    # Bar counter
    draw.rectangle([margin + 100, height - margin - 120, margin + 350, height - margin - 80],
                  fill=color, outline='#3a3a3a', width=3)
    
    # Tables
    for i in range(3):
        x = margin + 120 + i * 150
        y = margin + 150
        # Table
        draw.rectangle([x, y, x + 60, y + 60],
                      fill=color, outline='#3a3a3a', width=2)
        # Chairs
        draw.rectangle([x - 15, y + 15, x - 5, y + 45],
                      fill=color, outline='#2a2a2a', width=1)
        draw.rectangle([x + 65, y + 15, x + 75, y + 45],
                      fill=color, outline='#2a2a2a', width=1)
    
    # Barrels in corner
    for i in range(2):
        bx = width - margin - 100 - i * 45
        by = margin + 80
        draw.ellipse([bx - 20, by - 25, bx + 20, by + 25],
                    fill=color, outline='#3a3a3a', width=2)


def add_library_furniture(draw, margin, width, height, color):
    """Add library-style furniture"""
    # Bookshelves along walls
    for i in range(4):
        # Left wall shelves
        draw.rectangle([margin + 60, margin + 80 + i * 100, margin + 110, margin + 160 + i * 100],
                      fill=color, outline='#3a3a3a', width=2)
        # Right wall shelves
        draw.rectangle([width - margin - 110, margin + 80 + i * 100, width - margin - 60, margin + 160 + i * 100],
                      fill=color, outline='#3a3a3a', width=2)
    
    # Central reading table
    draw.rectangle([width // 2 - 100, height // 2 - 40, width // 2 + 100, height // 2 + 40],
                  fill=color, outline='#3a3a3a', width=3)
    
    # Chairs around table
    for i in range(4):
        if i < 2:
            cx = width // 2 - 60 + i * 120
            cy = height // 2 - 55
        else:
            cx = width // 2 - 60 + (i - 2) * 120
            cy = height // 2 + 55
        draw.rectangle([cx - 15, cy - 8, cx + 15, cy + 8],
                      fill=color, outline='#2a2a2a', width=1)


def add_room_furniture(draw, description, margin, width, height, color, theme):
    """Add furniture based on room description"""
    # Determine what furniture to add
    items = []
    
    if 'crate' in description or 'box' in description:
        items.append('crates')
    if 'table' in description:
        items.append('table')
    if 'chest' in description or 'treasure' in description:
        items.append('chest')
    if 'pillar' in description or 'column' in description:
        items.append('pillars')
    if 'barrel' in description:
        items.append('barrels')
    if 'torch' in description or 'light' in description:
        items.append('torches')
    
    # Default to some furniture if nothing specific mentioned
    if not items:
        items = ['crates', 'barrels']
    
    # Place furniture
    if 'crates' in items:
        for i in range(2):
            cx = margin + 100 + i * 300
            cy = margin + 100
            draw.rectangle([cx, cy, cx + 45, cy + 45],
                          fill=color, outline='#3a3a3a', width=2)
    
    if 'table' in items:
        tx = width // 2 - 60
        ty = height // 2 - 30
        draw.rectangle([tx, ty, tx + 120, ty + 60],
                      fill=color, outline='#3a3a3a', width=2)
    
    if 'chest' in items:
        chx = margin + 80
        chy = height - margin - 100
        draw.rectangle([chx, chy, chx + 50, chy + 35],
                      fill=color, outline='#ccaa66', width=3)
    
    if 'pillars' in items:
        for i in range(2):
            for j in range(2):
                px = margin + 150 + i * 300
                py = margin + 120 + j * 240
                draw.ellipse([px - 20, py - 20, px + 20, py + 20],
                            fill=color, outline='#3a3a3a', width=3)
    
    if 'barrels' in items:
        for i in range(3):
            bx = width - margin - 120
            by = margin + 80 + i * 60
            draw.ellipse([bx - 18, by - 22, bx + 18, by + 22],
                        fill=color, outline='#3a3a3a', width=2)
    
    if 'torches' in items:
        # Wall torches
        positions = [
            (margin + 80, margin + 60),
            (width - margin - 80, margin + 60),
            (margin + 80, height - margin - 60),
            (width - margin - 80, height - margin - 60)
        ]
        for tx, ty in positions:
            draw.rectangle([tx - 5, ty - 20, tx + 5, ty + 20],
                          fill='#6a5a4a', outline='#3a2a1a', width=1)
            # Flame
            draw.polygon([(tx, ty - 25), (tx - 8, ty - 15), (tx + 8, ty - 15)],
                        fill='#ff8800', outline='#ff6600')

