import io
import base64
import random
from PIL import Image, ImageDraw
from ai_layout import get_map_layout


def generate_room_map(room_holder, theme_era="Medieval"):
    """Generate a detailed top-down D&D style battle map"""
    width = 800
    height = 600
    img = Image.new('RGB', (width, height), color='#2a2520')
    draw = ImageDraw.Draw(img)
    
    # Get current room info
    cur_x = room_holder._cur_pos_x
    cur_y = room_holder._cur_pos_y
    room_array = room_holder._array_of_rooms
    current_room = room_array[cur_y][cur_x]
    description = current_room._description.lower() if current_room._description else ""
    
    # Set theme colors (defaults; AI layout may override floor colors)
    theme_lower = theme_era.lower()
    if 'cyber' in theme_lower or 'sci' in theme_lower:
        floor_base = '#1a2a3a'
        floor_accent = '#0d1a25'
        wall_base = '#0a1520'
        wall_accent = '#152535'
        furniture_color = '#2a4a5a'
    elif 'steam' in theme_lower:
        floor_base = '#4a3a2a'
        floor_accent = '#3a2a1a'
        wall_base = '#2a1a0a'
        wall_accent = '#4a2a1a'
        furniture_color = '#6a4a3a'
    else:  # Medieval
        floor_base = '#5a4a3a'
        floor_accent = '#4a3a2a'
        wall_base = '#2a2520'
        wall_accent = '#3a3530'
        furniture_color = '#6a5545'
    
    # Seed for consistent generation per room
    random.seed(hash(f"{cur_x}_{cur_y}"))
    
    # Grid settings for tile-based drawing
    tile_size = 20
    margin = 60
    room_width = width - 2 * margin
    room_height = height - 2 * margin
    
    # Build exits map for AI
    cols = room_holder._cols
    rows = room_holder._rows
    exits_map = {
        'north': bool(cols > cur_y + 1 and room_array[cur_y + 1][cur_x] is not None),
        'south': bool(cur_y > 0 and room_array[cur_y - 1][cur_x] is not None),
        'east': bool(rows > cur_x + 1 and room_array[cur_y][cur_x + 1] is not None),
        'west': bool(cur_x > 0 and room_array[cur_y][cur_x - 1] is not None),
    }

    # Fast path: avoid network calls for layout to reduce latency
    use_ai_layout = False  # set True to let the AI suggest colors/props
    if use_ai_layout:
        layout = get_map_layout(description, theme_era, exits_map)
    else:
        layout = {"room_type": "chamber", "floor": {}}

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

    # Draw floor with detailed tiles
    for y in range(margin, height - margin, tile_size):
        for x in range(margin, width - margin, tile_size):
            # Add variation
            shade = random.randint(-12, 12)
            r = min(255, max(0, int(floor_base[1:3], 16) + shade))
            g = min(255, max(0, int(floor_base[3:5], 16) + shade))
            b = min(255, max(0, int(floor_base[5:7], 16) + shade))
            color = f'#{r:02x}{g:02x}{b:02x}'
            
            # Draw tile
            draw.rectangle([x, y, x + tile_size - 1, y + tile_size - 1],
                          fill=color, outline=floor_accent, width=1)
            
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
    
    # Draw walls based on room type
    if has_alley:
        # Narrow alley with buildings on sides
        alley_width = 200
        alley_x = width // 2 - alley_width // 2
        
        # Left wall/building
        draw_stone_wall(draw, margin, margin, alley_x - 20, height - margin, wall_base, wall_accent)
        
        # Right wall/building
        draw_stone_wall(draw, alley_x + alley_width + 20, margin, width - margin, height - margin, wall_base, wall_accent)
        
        # Add details to buildings
        for i in range(3):
            y_pos = margin + 80 + i * 150
            # Windows/features on left
            draw.rectangle([margin + 20, y_pos, margin + 60, y_pos + 60],
                          fill='#1a1a1a', outline=wall_accent, width=3)
            # Windows/features on right
            draw.rectangle([width - margin - 60, y_pos, width - margin - 20, y_pos + 60],
                          fill='#1a1a1a', outline=wall_accent, width=3)
        
    elif has_tavern or has_library:
        # Room with multiple areas
        # Main walls
        wall_thickness = 25
        
        # Outer walls
        if not has_north:
            draw_stone_wall(draw, margin, margin, width - margin, margin + wall_thickness, wall_base, wall_accent)
        if not has_south:
            draw_stone_wall(draw, margin, height - margin - wall_thickness, width - margin, height - margin, wall_base, wall_accent)
        if not has_west:
            draw_stone_wall(draw, margin, margin, margin + wall_thickness, height - margin, wall_base, wall_accent)
        if not has_east:
            draw_stone_wall(draw, width - margin - wall_thickness, margin, width - margin, height - margin, wall_base, wall_accent)
        
        # Add furniture (disabled unless draw_furniture is True)
        if draw_furniture:
            if has_tavern:
                add_tavern_furniture(draw, margin, width, height, furniture_color)
            elif has_library:
                add_library_furniture(draw, margin, width, height, furniture_color)
        
    else:
        # Standard room with walls
        wall_thickness = 25
        
        # Draw walls with openings for exits
        if not has_north:
            draw_stone_wall(draw, margin, margin, width - margin, margin + wall_thickness, wall_base, wall_accent)
        else:
            # Wall with door opening
            door_width = 80
            door_x = width // 2 - door_width // 2
            draw_stone_wall(draw, margin, margin, door_x - 10, margin + wall_thickness, wall_base, wall_accent)
            draw_stone_wall(draw, door_x + door_width + 10, margin, width - margin, margin + wall_thickness, wall_base, wall_accent)
            draw_door(draw, door_x, margin, door_width, wall_thickness, 'north', furniture_color)
        
        if not has_south:
            draw_stone_wall(draw, margin, height - margin - wall_thickness, width - margin, height - margin, wall_base, wall_accent)
        else:
            door_width = 80
            door_x = width // 2 - door_width // 2
            draw_stone_wall(draw, margin, height - margin - wall_thickness, door_x - 10, height - margin, wall_base, wall_accent)
            draw_stone_wall(draw, door_x + door_width + 10, height - margin - wall_thickness, width - margin, height - margin, wall_base, wall_accent)
            draw_door(draw, door_x, height - margin - wall_thickness, door_width, wall_thickness, 'south', furniture_color)
        
        if not has_west:
            draw_stone_wall(draw, margin, margin, margin + wall_thickness, height - margin, wall_base, wall_accent)
        else:
            door_height = 80
            door_y = height // 2 - door_height // 2
            draw_stone_wall(draw, margin, margin, margin + wall_thickness, door_y - 10, wall_base, wall_accent)
            draw_stone_wall(draw, margin, door_y + door_height + 10, margin + wall_thickness, height - margin, wall_base, wall_accent)
            draw_door(draw, margin, door_y, wall_thickness, door_height, 'west', furniture_color)
        
        if not has_east:
            draw_stone_wall(draw, width - margin - wall_thickness, margin, width - margin, height - margin, wall_base, wall_accent)
        else:
            door_height = 80
            door_y = height // 2 - door_height // 2
            draw_stone_wall(draw, width - margin - wall_thickness, margin, width - margin, door_y - 10, wall_base, wall_accent)
            draw_stone_wall(draw, width - margin - wall_thickness, door_y + door_height + 10, width - margin, height - margin, wall_base, wall_accent)
            draw_door(draw, width - margin - wall_thickness, door_y, wall_thickness, door_height, 'east', furniture_color)
        
        # If AI provided props, draw them; otherwise fallback to heuristic furniture
        if draw_furniture:
            props = layout.get('props') or []
            if props:
                for p in props:
                    _draw_prop(draw, p, margin, width, height, furniture_color, theme_lower)
            else:
                add_room_furniture(draw, description, margin, width, height, furniture_color, theme_lower)
    
    # Draw player marker
    player_x = width // 2
    player_y = height // 2
    draw.ellipse([player_x - 12, player_y - 12, player_x + 12, player_y + 12],
                fill='#ff3333', outline='#ffffff', width=3)
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    style = 'border:2px solid #444; border-radius:8px;'
    return f'<img src="data:image/png;base64,{img_str}" style="{style}"/>'


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
    """Draw a textured stone wall"""
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
