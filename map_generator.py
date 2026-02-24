import io
import base64
import random
import math
from PIL import Image, ImageDraw
from ai_layout import get_map_layout


# ─── Classification helpers ───────────────────────────────────────────────────

def _classify_room_shape(identity_lower):
    """Return one of: 'corridor', 'large_hall', 'standard'."""
    if any(k in identity_lower for k in ['corridor', 'passage', 'hallway', 'tunnel', 'bridge']):
        return 'corridor'
    if any(k in identity_lower for k in ['great hall', 'grand hall', 'throne', 'cathedral',
                                          'market', 'bazaar', 'banquet hall']):
        return 'large_hall'
    return 'standard'


def _classify_interior(identity_lower, description):
    """Return an interior type string based on room identity keywords."""
    if any(k in identity_lower for k in ['library', 'archive', 'study', 'scriptorium', 'reading room']):
        return 'library'
    if any(k in identity_lower for k in ['crypt', 'tomb', 'mausoleum', 'burial', 'catacomb', 'ossuary']):
        return 'crypt'
    if any(k in identity_lower for k in ['chapel', 'shrine', 'temple', 'altar', 'sanctuary', 'church']):
        return 'chapel'
    if any(k in identity_lower for k in ['market', 'bazaar', 'trading', 'merchant', 'bazaar']):
        return 'market'
    if any(k in identity_lower for k in ['boiler', 'engine room', 'furnace', 'foundry', 'factory', 'boiler hall']):
        return 'boiler'
    if any(k in identity_lower for k in ['tavern', 'inn', 'alehouse', 'pub']):
        return 'tavern'
    if any(k in identity_lower for k in ['throne', 'court', 'audience', 'great hall', 'royal chamber']):
        return 'throne'
    if any(k in identity_lower for k in ['prison', 'cell', 'holding', 'lockup', 'dungeon cell']):
        return 'prison'
    if any(k in identity_lower for k in ['laborator', 'alchemist', 'research', 'experiment', 'workshop']):
        return 'laboratory'
    if any(k in identity_lower for k in ['armory', 'arsenal', 'barracks', 'weapon rack', 'forge']):
        return 'armory'
    if any(k in identity_lower for k in ['server', 'data center', 'mainframe', 'command center', 'control room']):
        return 'server'
    if any(k in identity_lower for k in ['treasure', 'vault', 'treasury']):
        return 'treasury'
    return 'generic'


def _get_wall_style(theme_lower, interior_type):
    """Determine wall drawing style from theme and room type."""
    if 'cyber' in theme_lower or 'sci' in theme_lower:
        return 'metal'
    if 'steam' in theme_lower:
        return 'copper'
    if interior_type in ('crypt', 'prison'):
        return 'cave'
    return 'stone'


# ─── Wall drawing functions ───────────────────────────────────────────────────

def draw_stone_wall(draw, x1, y1, x2, y2, base_color, accent_color):
    """Draw a textured stone wall."""
    x1, y1, x2, y2 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
    if x2 - x1 < 1 or y2 - y1 < 1:
        return
    draw.rectangle([x1, y1, x2, y2], fill=base_color, outline=accent_color, width=2)
    for i in range(int((x2 - x1) / 40)):
        for j in range(int((y2 - y1) / 40)):
            sx = x1 + i * 40 + random.randint(-5, 5)
            sy = y1 + j * 40 + random.randint(-5, 5)
            draw.rectangle([sx, sy, sx + 35, sy + 35], outline=accent_color, width=1)


def draw_metal_wall(draw, x1, y1, x2, y2, base_color, accent_color):
    """Draw a sci-fi metal panel wall with rivets and neon trim."""
    x1, y1, x2, y2 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
    if x2 - x1 < 1 or y2 - y1 < 1:
        return
    draw.rectangle([x1, y1, x2, y2], fill=base_color, outline=accent_color, width=2)
    w, h = max(1, x2 - x1), max(1, y2 - y1)
    panel_w = max(20, w // 4)
    panel_h = max(15, h // 3)
    for px in range(x1 + panel_w, x2, panel_w):
        draw.line([px, y1, px, y2], fill=accent_color, width=1)
    for py in range(y1 + panel_h, y2, panel_h):
        draw.line([x1, py, x2, py], fill=accent_color, width=1)
    for px in range(x1 + panel_w, x2, panel_w):
        for py in range(y1 + panel_h, y2, panel_h):
            draw.ellipse([px - 3, py - 3, px + 3, py + 3], fill='#2a2a2a', outline=accent_color)
    draw.rectangle([x1, y1, x2, y2], outline='#00ccaa', width=1)


def draw_copper_wall(draw, x1, y1, x2, y2, base_color, accent_color):
    """Draw a steampunk copper/wood wall with bolts."""
    x1, y1, x2, y2 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
    if x2 - x1 < 1 or y2 - y1 < 1:
        return
    draw.rectangle([x1, y1, x2, y2], fill=base_color, outline=accent_color, width=2)
    h = max(1, y2 - y1)
    plank_h = max(12, h // 4)
    for py in range(y1 + plank_h, y2, plank_h):
        draw.line([x1, py, x2, py], fill=accent_color, width=2)
    bolt_color = '#b87333'
    bolt_hi = '#d4915a'
    for px in range(x1 + 12, x2, 28):
        for py in range(y1 + 8, y2, plank_h):
            draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=bolt_color, outline=bolt_hi, width=1)


def draw_cave_wall(draw, x1, y1, x2, y2, base_color, accent_color):
    """Draw rough, organic cave/crypt walls."""
    x1, y1, x2, y2 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
    if x2 - x1 < 1 or y2 - y1 < 1:
        return
    draw.rectangle([x1, y1, x2, y2], fill='#1a1510', outline='#2a2018', width=2)
    area = max(1, (x2 - x1) * (y2 - y1))
    for _ in range(max(1, area // 300)):
        rx = random.randint(x1, max(x1, x2 - 10))
        ry = random.randint(y1, max(y1, y2 - 8))
        rw = random.randint(4, 18)
        rh = random.randint(3, 12)
        draw.ellipse([rx, ry, rx + rw, ry + rh], fill='#2a2018')
    for _ in range(max(1, (x2 - x1 + y2 - y1) // 60)):
        cx = random.randint(x1, x2)
        cy = random.randint(y1, y2)
        draw.line([cx, cy, cx + random.randint(-20, 20), cy + random.randint(-20, 20)],
                  fill='#0a0a08', width=1)


def _wall_fn_for_style(style):
    return {
        'metal': draw_metal_wall,
        'copper': draw_copper_wall,
        'cave': draw_cave_wall,
    }.get(style, draw_stone_wall)


def draw_door(draw, x, y, w, h, direction, color):
    """Draw a door opening."""
    if direction in ['north', 'south']:
        draw.rectangle([x + 10, y, x + w - 10, y + h], fill=color, outline='#3a3a3a', width=2)
        hx, hy = x + w // 2, y + h // 2
        draw.ellipse([hx - 4, hy - 4, hx + 4, hy + 4], fill='#ccaa66')
    else:
        draw.rectangle([x, y + 10, x + w, y + h - 10], fill=color, outline='#3a3a3a', width=2)
        hx, hy = x + w // 2, y + h // 2
        draw.ellipse([hx - 4, hy - 4, hx + 4, hy + 4], fill='#ccaa66')


def _draw_all_walls(draw, wall_style, has_north, has_south, has_east, has_west,
                    margin, width, height, wall_base, wall_accent, furniture_color, wall_thickness):
    """Draw all four outer walls with appropriate exits."""
    wall_fn = _wall_fn_for_style(wall_style)
    door_w = 80
    door_h = 80

    # North wall
    if not has_north:
        wall_fn(draw, margin, margin, width - margin, margin + wall_thickness, wall_base, wall_accent)
    else:
        dx = width // 2 - door_w // 2
        wall_fn(draw, margin, margin, dx - 10, margin + wall_thickness, wall_base, wall_accent)
        wall_fn(draw, dx + door_w + 10, margin, width - margin, margin + wall_thickness, wall_base, wall_accent)
        draw_door(draw, dx, margin, door_w, wall_thickness, 'north', furniture_color)

    # South wall
    if not has_south:
        wall_fn(draw, margin, height - margin - wall_thickness, width - margin, height - margin, wall_base, wall_accent)
    else:
        dx = width // 2 - door_w // 2
        wall_fn(draw, margin, height - margin - wall_thickness, dx - 10, height - margin, wall_base, wall_accent)
        wall_fn(draw, dx + door_w + 10, height - margin - wall_thickness, width - margin, height - margin, wall_base, wall_accent)
        draw_door(draw, dx, height - margin - wall_thickness, door_w, wall_thickness, 'south', furniture_color)

    # West wall
    if not has_west:
        wall_fn(draw, margin, margin, margin + wall_thickness, height - margin, wall_base, wall_accent)
    else:
        dy = height // 2 - door_h // 2
        wall_fn(draw, margin, margin, margin + wall_thickness, dy - 10, wall_base, wall_accent)
        wall_fn(draw, margin, dy + door_h + 10, margin + wall_thickness, height - margin, wall_base, wall_accent)
        draw_door(draw, margin, dy, wall_thickness, door_h, 'west', furniture_color)

    # East wall
    if not has_east:
        wall_fn(draw, width - margin - wall_thickness, margin, width - margin, height - margin, wall_base, wall_accent)
    else:
        dy = height // 2 - door_h // 2
        wall_fn(draw, width - margin - wall_thickness, margin, width - margin, dy - 10, wall_base, wall_accent)
        wall_fn(draw, width - margin - wall_thickness, dy + door_h + 10, width - margin, height - margin, wall_base, wall_accent)
        draw_door(draw, width - margin - wall_thickness, dy, wall_thickness, door_h, 'east', furniture_color)


# ─── Interior shared helpers ──────────────────────────────────────────────────

def _draw_pillar(draw, x, y, radius, color):
    """Draw a circular stone pillar."""
    draw.ellipse([x - radius, y - radius, x + radius, y + radius],
                 fill=color, outline='#3a3a3a', width=3)
    inner = radius - 5
    if inner > 2:
        draw.ellipse([x - inner, y - inner, x + inner, y + inner],
                     fill=None, outline='#5a5a5a', width=1)


def _draw_gear(draw, cx, cy, radius, color):
    """Draw a simple gear wheel."""
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 fill=color, outline='#2a2a2a', width=2)
    hub = max(3, radius // 3)
    draw.ellipse([cx - hub, cy - hub, cx + hub, cy + hub],
                 fill='#2a2a2a', outline=color, width=1)
    for i in range(8):
        angle = i * math.pi / 4
        tx = cx + int((radius - 2) * math.cos(angle))
        ty = cy + int((radius - 2) * math.sin(angle))
        draw.ellipse([tx - 5, ty - 5, tx + 5, ty + 5], fill=color, outline='#2a2a2a', width=1)


def _draw_bookshelf(draw, x, y, w, h, color, vertical=False):
    """Draw a bookshelf with colored book spines."""
    draw.rectangle([x, y, x + w, y + h], fill=color, outline='#3a3a3a', width=2)
    book_colors = ['#8B1a1a', '#1a5a8B', '#2a7a2a', '#8B6a1a', '#5a1a8B']
    if vertical:
        shelf_gap = max(10, h // 4)
        for sy in range(y + shelf_gap, y + h, shelf_gap):
            draw.line([x + 2, sy, x + w - 2, sy], fill='#2a2a2a', width=1)
        bw = max(3, w // 5)
        for i, bc in enumerate(book_colors[: max(1, w // bw)]):
            bx = x + 2 + i * bw
            if bx + bw - 2 <= x + w - 2:
                draw.rectangle([bx, y + 3, bx + bw - 2, y + h - 3], fill=bc, outline='#1a1a1a', width=1)
    else:
        shelf_gap = max(10, w // 4)
        for sx in range(x + shelf_gap, x + w, shelf_gap):
            draw.line([sx, y + 2, sx, y + h - 2], fill='#2a2a2a', width=1)
        bh = max(3, h // 4)
        for i, bc in enumerate(book_colors[: max(1, h // bh)]):
            by = y + 2 + i * bh
            if by + bh - 2 <= y + h - 2:
                draw.rectangle([x + 3, by, x + w - 3, by + bh - 2], fill=bc, outline='#1a1a1a', width=1)


def _draw_shelf_with_bottles(draw, x1, y1, x2, y2, color):
    """Draw a shelf holding potion bottles."""
    x1, y1, x2, y2 = min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)
    if x2 - x1 < 1 or y2 - y1 < 1:
        return
    draw.rectangle([x1, y1, x2, y2], fill=color, outline='#3a3a3a', width=2)
    flask_colors = ['#2a6a8a', '#8a2a2a', '#2a8a2a', '#8a8a2a', '#6a2a8a']
    for i, fc in enumerate(flask_colors):
        bx = x1 + 15 + i * 30
        if bx + 14 > x2 - 10:
            break
        by = y1 + 5
        draw.ellipse([bx, by + 4, bx + 14, by + 18], fill=fc, outline='#2a2a2a', width=1)
        draw.rectangle([bx + 5, by, bx + 9, by + 6], fill='#8B8B8B', outline='#5a5a5a')


# ─── Interior layout functions ────────────────────────────────────────────────

def _interior_library(draw, margin, width, height, color, theme):
    """Bookshelves along walls, central reading table, candles."""
    wt = 30
    # North and south wall bookshelves
    for i in range(3):
        off = 100 + i * 160
        _draw_bookshelf(draw, margin + wt + off, margin + wt, 60, 28, color)
        _draw_bookshelf(draw, margin + wt + off, height - margin - wt - 28, 60, 28, color)
    # West and east wall bookshelves
    for i in range(2):
        off = 100 + i * 160
        _draw_bookshelf(draw, margin + wt, margin + wt + off, 28, 60, color, vertical=True)
        _draw_bookshelf(draw, width - margin - wt - 28, margin + wt + off, 28, 60, color, vertical=True)
    # Central reading table
    cx, cy = width // 2, height // 2
    draw.rectangle([cx - 80, cy - 35, cx + 80, cy + 35], fill=color, outline='#3a3a3a', width=3)
    for chx, chy in [(cx - 80, cy), (cx + 80, cy), (cx, cy - 35), (cx, cy + 35)]:
        draw.rectangle([chx - 12, chy - 8, chx + 12, chy + 8], fill=color, outline='#2a2a2a', width=1)
    # Candles on table
    for cax in [cx - 40, cx + 40]:
        draw.rectangle([cax - 3, cy - 12, cax + 3, cy - 2], fill='#ccaa77', outline='#8a6a3a')
        draw.polygon([(cax, cy - 18), (cax - 5, cy - 12), (cax + 5, cy - 12)], fill='#ff8800')


def _interior_crypt(draw, margin, width, height, color, theme):
    """Sarcophagi, corner pillars, central altar with candles."""
    wt = 30
    cx, cy = width // 2, height // 2
    # Corner pillars
    for px, py in [
        (margin + wt + 22, margin + wt + 22),
        (width - margin - wt - 22, margin + wt + 22),
        (margin + wt + 22, height - margin - wt - 22),
        (width - margin - wt - 22, height - margin - wt - 22),
    ]:
        _draw_pillar(draw, px, py, 20, color)
    # Two sarcophagi
    sarc = '#6a6a5a'
    for sx in [cx - 130, cx + 70]:
        draw.rectangle([sx, cy - 30, sx + 60, cy + 30], fill=sarc, outline='#3a3a3a', width=3)
        draw.ellipse([sx + 18, cy - 18, sx + 42, cy + 2], fill='#4a4a3a', outline='#2a2a2a', width=1)
        draw.line([sx + 30, cy + 8, sx + 30, cy + 25], fill='#5a5a4a', width=2)
        draw.line([sx + 20, cy + 16, sx + 40, cy + 16], fill='#5a5a4a', width=2)
    # Central altar
    draw.rectangle([cx - 35, cy - 18, cx + 35, cy + 18], fill='#4a4a3a', outline='#7a7a6a', width=3)
    # Candles on altar
    for ax in [cx - 20, cx, cx + 20]:
        draw.rectangle([ax - 3, cy - 28, ax + 3, cy - 18], fill='#ccaa77', outline='#8a6a3a')
        draw.polygon([(ax, cy - 34), (ax - 5, cy - 28), (ax + 5, cy - 28)], fill='#ff8800')
    # Corner cobweb suggestions
    for wx, wy, dx, dy in [(margin + 32, margin + 32, 1, 1), (width - margin - 32, margin + 32, -1, 1)]:
        for i in range(4):
            draw.line([wx, wy, wx + dx * (20 - i * 4), wy + dy * (20 - i * 4)], fill='#4a4a4a', width=1)


def _interior_chapel(draw, margin, width, height, color, theme):
    """Pews in rows, altar at north end, torches on sides."""
    wt = 35
    cx = width // 2
    # Altar at north end
    altar_y = margin + wt + 10
    draw.rectangle([cx - 60, altar_y, cx + 60, altar_y + 35], fill='#8a7a5a', outline='#ccaa66', width=3)
    # Altar candles
    for ax in [cx - 40, cx, cx + 40]:
        draw.rectangle([ax - 3, altar_y - 18, ax + 3, altar_y], fill='#e0c060', outline='#a07820')
        draw.polygon([(ax, altar_y - 24), (ax - 5, altar_y - 18), (ax + 5, altar_y - 18)], fill='#ff9900')
    # Cross above altar
    draw.line([cx, altar_y - 40, cx, altar_y - 10], fill='#ccaa66', width=4)
    draw.line([cx - 20, altar_y - 30, cx + 20, altar_y - 30], fill='#ccaa66', width=4)
    # Pews (two columns with center aisle)
    pew_y = margin + wt + 70
    for row in range(4):
        py = pew_y + row * 65
        if py + 18 > height - margin - wt - 20:
            break
        draw.rectangle([margin + wt + 20, py, cx - 30, py + 18], fill=color, outline='#2a2a2a', width=2)
        draw.rectangle([cx + 30, py, width - margin - wt - 20, py + 18], fill=color, outline='#2a2a2a', width=2)
    # Wall torches
    for ty in [margin + wt + 60, height // 2, height - margin - wt - 60]:
        for tx in [margin + wt + 15, width - margin - wt - 15]:
            draw.rectangle([tx - 4, ty - 18, tx + 4, ty + 18], fill='#6a5a4a', outline='#3a2a1a')
            draw.polygon([(tx, ty - 24), (tx - 7, ty - 18), (tx + 7, ty - 18)], fill='#ff8800', outline='#ff6600')


def _interior_market(draw, margin, width, height, color, theme):
    """Market stalls in two rows flanking a central aisle, well in center."""
    wt = 30
    cx, cy = width // 2, height // 2
    stall_w, stall_h = 90, 55
    stall_lx = margin + wt + 20
    stall_rx = width - margin - wt - 20 - stall_w
    canopy_cols = ['#8B1a1a', '#1a5a8B', '#2a7a2a']
    for i in range(3):
        sy = margin + wt + 30 + i * 72
        if sy + stall_h > height - margin - wt:
            break
        for sx, canopy_i in [(stall_lx, i), (stall_rx, i + 1)]:
            draw.rectangle([sx, sy, sx + stall_w, sy + stall_h], fill=color, outline='#3a3a3a', width=2)
            c = canopy_cols[canopy_i % len(canopy_cols)]
            draw.polygon([(sx, sy), (sx + stall_w, sy), (sx + stall_w // 2, sy - 15)],
                         fill=c, outline='#2a2a2a')
            for gi in range(3):
                gx = sx + 10 + gi * 25
                draw.rectangle([gx, sy + 20, gx + 18, sy + 38], fill='#8B8B6a', outline='#5a5a3a', width=1)
    # Well/fountain in center
    draw.ellipse([cx - 25, cy - 25, cx + 25, cy + 25], fill='#2a5a7a', outline='#4a8aaa', width=3)
    draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill='#1a3a5a', outline='#2a6a8a', width=1)


def _interior_boiler(draw, margin, width, height, color, theme):
    """Boilers, pipes, gear wheels for industrial rooms."""
    cx, cy = width // 2, height // 2
    boiler_color = '#6a5a3a' if 'steam' in theme else '#4a4a5a'
    pipe_color = '#b87333' if 'steam' in theme else '#3a5a5a'
    # Two large boilers
    for bx in [cx - 140, cx + 80]:
        draw.rectangle([bx, cy - 60, bx + 60, cy + 60], fill=boiler_color, outline='#3a3a2a', width=3)
        draw.ellipse([bx, cy - 70, bx + 60, cy - 50], fill=boiler_color, outline='#5a5a3a', width=2)
        draw.ellipse([bx, cy + 50, bx + 60, cy + 70], fill=boiler_color, outline='#5a5a3a', width=2)
        # Pressure gauge
        draw.ellipse([bx + 18, cy - 20, bx + 42, cy + 4], fill='#c0c0c0', outline='#808080', width=2)
        draw.line([bx + 30, cy - 8, bx + 38, cy - 4], fill='#cc0000', width=2)
        # Rivets
        for ry_off in range(-40, 60, 20):
            draw.ellipse([bx + 5, cy + ry_off, bx + 13, cy + ry_off + 8], fill='#5a5a3a', outline='#3a3a2a')
            draw.ellipse([bx + 47, cy + ry_off, bx + 55, cy + ry_off + 8], fill='#5a5a3a', outline='#3a3a2a')
    # Floor pipes
    for py_off in [-20, 0, 20]:
        lw = 6 - abs(py_off) // 10
        draw.line([margin + 30, height - margin - 55 + py_off, width - margin - 30, height - margin - 55 + py_off],
                  fill=pipe_color, width=max(1, lw))
    # Pipe joints
    for px in range(margin + 80, width - margin - 80, 100):
        draw.ellipse([px - 10, height - margin - 75, px + 10, height - margin - 35],
                     fill=pipe_color, outline='#2a2a2a', width=2)
    # Gear wheels on east/west walls
    for gx, gy in [(margin + 50, cy), (width - margin - 50, cy)]:
        _draw_gear(draw, gx, gy, 28, pipe_color)
    # Steam vents on north wall
    for sx in [cx - 80, cx + 80]:
        sy = margin + 55
        draw.rectangle([sx - 6, sy, sx + 6, sy + 30], fill=pipe_color, outline='#2a2a2a', width=2)
        for i in range(3):
            sr = 7 + i * 5
            draw.ellipse([sx - sr, sy - i * 14 - sr, sx + sr, sy - i * 14 + sr],
                         fill=None, outline='#c0c0c0', width=1)


def _interior_tavern(draw, margin, width, height, color, theme):
    """Bar counter along south wall, scattered tables, barrels in corners."""
    wt = 30
    # Bar counter
    bar_y = height - margin - wt - 50
    draw.rectangle([margin + wt + 20, bar_y, width - margin - wt - 20, bar_y + 45],
                   fill=color, outline='#3a2a1a', width=3)
    draw.rectangle([margin + wt + 20, bar_y, width - margin - wt - 20, bar_y + 8],
                   fill='#8B6a3a', outline='#5a4a2a', width=1)
    # Mugs on bar
    for mx in range(margin + wt + 60, width - margin - wt - 60, 80):
        draw.rectangle([mx - 8, bar_y - 20, mx + 8, bar_y], fill='#8B8B5a', outline='#5a5a3a', width=1)
    # Tables
    table_positions = [
        (margin + 120, margin + 100),
        (width // 2, margin + 100),
        (width - margin - 140, margin + 100),
        (margin + 160, height // 2 - 30),
        (width - margin - 160, height // 2 - 30),
    ]
    for tx, ty in table_positions:
        if ty + 20 < bar_y - 20:
            draw.rectangle([tx - 30, ty - 20, tx + 30, ty + 20], fill=color, outline='#3a2a1a', width=2)
            for chx, chy in [(tx - 40, ty), (tx + 40, ty), (tx, ty - 28), (tx, ty + 28)]:
                draw.rectangle([chx - 10, chy - 7, chx + 10, chy + 7], fill=color, outline='#2a1a0a', width=1)
    # Barrels in NW and NE corners
    for bx in [margin + wt + 15, width - margin - wt - 55]:
        for bi in range(3):
            by = margin + wt + 20 + bi * 45
            draw.ellipse([bx, by, bx + 40, by + 40], fill='#5a3a1a', outline='#3a2a0a', width=2)
            draw.line([bx, by + 20, bx + 40, by + 20], fill='#3a2a0a', width=2)
            draw.line([bx, by + 10, bx + 40, by + 10], fill='#3a2a0a', width=1)
            draw.line([bx, by + 30, bx + 40, by + 30], fill='#3a2a0a', width=1)


def _interior_throne(draw, margin, width, height, color, theme):
    """Throne at north end, grand columns, red carpet down center."""
    cx, cy = width // 2, height // 2
    wt = 35
    # Red carpet
    draw.rectangle([cx - 40, margin + wt + 40, cx + 40, height - margin - wt],
                   fill='#6a1a1a', outline='#8a2a2a', width=2)
    # Carpet border details
    for y in range(margin + wt + 55, height - margin - wt, 30):
        draw.rectangle([cx - 40 + 5, y, cx - 40 + 12, y + 10], fill='#8a3a3a')
        draw.rectangle([cx + 40 - 12, y, cx + 40 - 5, y + 10], fill='#8a3a3a')
    # Grand columns (4)
    for px, py in [
        (margin + wt + 60, margin + wt + 60),
        (width - margin - wt - 60, margin + wt + 60),
        (margin + wt + 60, height - margin - wt - 60),
        (width - margin - wt - 60, height - margin - wt - 60),
    ]:
        _draw_pillar(draw, px, py, 22, '#8B8B7a')
    # Throne
    throne_x, throne_y = cx - 35, margin + wt + 15
    draw.rectangle([throne_x, throne_y + 25, throne_x + 70, throne_y + 55],
                   fill='#6a5a1a', outline='#ccaa33', width=3)
    draw.rectangle([throne_x + 5, throne_y, throne_x + 65, throne_y + 30],
                   fill='#6a5a1a', outline='#ccaa33', width=3)
    # Crown points
    pts = [(throne_x + 15, throne_y), (throne_x + 25, throne_y - 14),
           (throne_x + 35, throne_y - 5), (throne_x + 45, throne_y - 14),
           (throne_x + 55, throne_y)]
    draw.line(pts, fill='#ccaa33', width=3)
    # Armrests
    draw.rectangle([throne_x, throne_y + 25, throne_x + 12, throne_y + 45],
                   fill='#8a7a2a', outline='#ccaa33', width=2)
    draw.rectangle([throne_x + 58, throne_y + 25, throne_x + 70, throne_y + 45],
                   fill='#8a7a2a', outline='#ccaa33', width=2)


def _interior_prison(draw, margin, width, height, color, theme):
    """Cell bars dividing sections, chains on north wall."""
    cx, cy = width // 2, height // 2
    wt = 35
    bar_color = '#4a4a4a'
    # Left cell block bars
    cx1, cx2 = margin + wt + 20, cx - 40
    for bx in range(cx1 + 18, cx2, 18):
        draw.line([bx, margin + wt, bx, height - margin - wt], fill=bar_color, width=3)
    draw.line([cx1, cy, cx2, cy], fill=bar_color, width=6)
    # Right cell block bars
    cx3, cx4 = cx + 40, width - margin - wt - 20
    for bx in range(cx3 + 18, cx4, 18):
        draw.line([bx, margin + wt, bx, height - margin - wt], fill=bar_color, width=3)
    draw.line([cx3, cy, cx4, cy], fill=bar_color, width=6)
    # Chains on north wall
    for chx in [margin + wt + 60, width - margin - wt - 60]:
        chy = margin + wt + 40
        draw.line([chx, chy, chx, chy + 30], fill='#6a6a6a', width=3)
        draw.line([chx + 15, chy, chx + 15, chy + 30], fill='#6a6a6a', width=3)
        draw.ellipse([chx - 8, chy + 25, chx + 8, chy + 38], fill=None, outline='#6a6a6a', width=3)
        draw.ellipse([chx + 7, chy + 25, chx + 23, chy + 38], fill=None, outline='#6a6a6a', width=3)
    # Straw pile in left cell
    for sx in range(cx1 + 20, min(cx2 - 10, cx1 + 80), 8):
        draw.line([sx, height - margin - wt - 25, sx + 5, height - margin - wt - 10],
                  fill='#6a5a2a', width=1)


def _interior_laboratory(draw, margin, width, height, color, theme):
    """Workbenches, shelves with potions, central alchemy circle."""
    cx, cy = width // 2, height // 2
    wt = 35
    lab_color = '#5a6a5a' if 'steam' not in theme else '#5a5a3a'
    # Workbenches on west and east sides
    for wx in [margin + wt, width - margin - wt - 80]:
        draw.rectangle([wx, margin + wt + 50, wx + 80, height - margin - wt - 50],
                       fill=lab_color, outline='#3a4a3a', width=3)
        for ei in range(3):
            ey = margin + wt + 70 + ei * 80
            if ey + 30 < height - margin - wt - 50:
                # Flask
                draw.ellipse([wx + 15, ey, wx + 35, ey + 20], fill='#2a6a8a', outline='#1a4a6a', width=2)
                draw.rectangle([wx + 23, ey - 12, wx + 27, ey], fill='#5a8aaa', outline='#3a6a8a')
                # Bubble
                draw.ellipse([wx + 30, ey + 3, wx + 38, ey + 11], fill='#3a8aaa')
    # North shelf with bottles
    _draw_shelf_with_bottles(draw, margin + wt + 30, margin + wt + 8, width - margin - wt - 30, margin + wt + 32, lab_color)
    # Alchemy circle on floor
    for r in [50, 35, 20]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=None, outline='#4a8a5a', width=1)
    for i in range(6):
        angle = i * math.pi / 3
        draw.line([cx + int(20 * math.cos(angle)), cy + int(20 * math.sin(angle)),
                   cx + int(48 * math.cos(angle)), cy + int(48 * math.sin(angle))],
                  fill='#4a8a5a', width=1)


def _interior_armory(draw, margin, width, height, color, theme):
    """Weapon racks on north wall, armor stands, shields on east wall."""
    cx, cy = width // 2, height // 2
    wt = 35
    metal = '#7a7a8a'
    rack_y = margin + wt + 10
    # Weapon racks
    for rx in range(margin + wt + 30, width - margin - wt - 30, 90):
        draw.line([rx, rack_y + 20, rx + 70, rack_y + 20], fill='#5a5a5a', width=4)
        draw.line([rx + 35, rack_y + 20, rx + 35, rack_y + 50], fill='#5a5a5a', width=3)
        for wi, wx in enumerate(range(rx + 10, rx + 65, 18)):
            weapon_l = 35 + wi * 5
            draw.line([wx, rack_y + 20, wx, rack_y + weapon_l], fill=metal, width=2)
            draw.rectangle([wx - 4, rack_y + 20, wx + 4, rack_y + 26], fill=metal, outline='#3a3a3a')
    # Armor stands
    for ax in [margin + wt + 60, width - margin - wt - 80]:
        ay = cy
        draw.ellipse([ax - 15, ay - 55, ax + 15, ay - 30], fill=metal, outline='#3a3a3a', width=2)
        draw.polygon([(ax - 20, ay - 30), (ax + 20, ay - 30), (ax + 25, ay + 20), (ax - 25, ay + 20)],
                     fill=metal, outline='#3a3a3a')
        draw.rectangle([ax - 15, ay + 20, ax - 3, ay + 55], fill=metal, outline='#3a3a3a', width=2)
        draw.rectangle([ax + 3, ay + 20, ax + 15, ay + 55], fill=metal, outline='#3a3a3a', width=2)
    # Shields on east wall
    shx = width - margin - wt - 18
    for si in range(3):
        sy = margin + wt + 60 + si * 100
        pts = [(shx, sy), (shx - 30, sy), (shx - 35, sy + 30),
               (shx - 15, sy + 50), (shx + 5, sy + 30)]
        draw.polygon(pts, fill='#5a5a6a', outline=metal, width=2)
        draw.line([shx - 15, sy + 10, shx - 15, sy + 38], fill='#ccaa33', width=2)
        draw.line([shx - 28, sy + 24, shx - 2, sy + 24], fill='#ccaa33', width=2)


def _interior_server(draw, margin, width, height, color, theme):
    """Server racks with blinking LEDs, cable channels, central terminal."""
    cx, cy = width // 2, height // 2
    wt = 35
    srv = '#1a1a2a'
    neon = '#00ccaa'
    rack_defs = [
        (margin + wt + 20, margin + wt + 30),
        (margin + wt + 120, margin + wt + 30),
        (cx + 20, margin + wt + 30),
        (cx + 120, margin + wt + 30),
    ]
    max_rh = min(200, height - 2 * margin - 2 * wt - 30)
    for rx, ry in rack_defs:
        rw, rh = 80, max_rh
        if rx + rw > width - margin - wt:
            break
        draw.rectangle([rx, ry, rx + rw, ry + rh], fill=srv, outline='#3a3a5a', width=2)
        unit_h = 15
        for ui in range(rh // (unit_h + 3)):
            uy = ry + 5 + ui * (unit_h + 3)
            if uy + unit_h > ry + rh - 5:
                break
            draw.rectangle([rx + 3, uy, rx + rw - 3, uy + unit_h], fill='#0a0a1a', outline='#2a2a4a', width=1)
            led = neon if random.random() > 0.3 else '#cc2222'
            draw.ellipse([rx + rw - 14, uy + 4, rx + rw - 7, uy + 11], fill=led)
            draw.ellipse([rx + rw - 22, uy + 4, rx + rw - 15, uy + 11], fill='#5a5a8a')
    # Cable channel on floor
    draw.rectangle([margin + wt, height - margin - wt - 25, width - margin - wt, height - margin - wt - 15],
                   fill='#0a0a1a', outline='#2a2a4a', width=2)
    for i, cc in enumerate(['#cc2222', '#2222cc', '#22cc22', '#cccc22']):
        draw.line([margin + wt + 10 + i * 15, height - margin - wt - 25,
                   width - margin - wt - 10 - i * 15, height - margin - wt - 15],
                  fill=cc, width=2)
    # Central terminal (offset from center)
    tx, ty = cx - 30, cy + 40
    draw.rectangle([tx, ty, tx + 60, ty + 40], fill='#0a0a1a', outline=neon, width=2)
    draw.rectangle([tx + 5, ty + 5, tx + 55, ty + 30], fill='#0a1a0a', outline='#1a3a1a', width=1)
    for li in range(4):
        ly = ty + 8 + li * 6
        lw = random.randint(10, 40)
        draw.line([tx + 5 + (50 - lw) // 2, ly, tx + 5 + (50 + lw) // 2, ly], fill=neon, width=1)


def _interior_treasury(draw, margin, width, height, color, theme):
    """Vault door on north wall, chests around room, coin piles."""
    cx, cy = width // 2, height // 2
    wt = 35
    gold = '#ccaa33'
    chest_c = '#8B5a1a'
    # Vault door on north wall
    vx, vy = cx - 45, margin + wt + 5
    draw.rectangle([vx, vy, vx + 90, vy + 60], fill='#4a4a4a', outline='#8a8a8a', width=4)
    draw.ellipse([vx + 30, vy + 10, vx + 60, vy + 40], fill='#5a5a5a', outline='#aaaaaa', width=3)
    draw.line([vx + 45, vy + 10, vx + 45, vy + 40], fill='#aaaaaa', width=2)
    draw.line([vx + 30, vy + 25, vx + 60, vy + 25], fill='#aaaaaa', width=2)
    # Chests
    for chx, chy in [
        (margin + wt + 30, margin + wt + 100),
        (width - margin - wt - 80, margin + wt + 100),
        (margin + wt + 30, cy + 30),
        (width - margin - wt - 80, cy + 30),
        (cx - 30, height - margin - wt - 80),
    ]:
        draw.rectangle([chx, chy + 15, chx + 50, chy + 40], fill=chest_c, outline='#5a3a0a', width=2)
        draw.rectangle([chx, chy, chx + 50, chy + 18], fill='#9B6a2a', outline='#5a3a0a', width=2)
        draw.rectangle([chx + 20, chy + 10, chx + 30, chy + 22], fill=gold, outline='#8a6a10', width=2)
        for ci in range(4):
            draw.ellipse([chx + 8 + ci * 10, chy + 5, chx + 16 + ci * 10, chy + 12],
                         fill=gold, outline='#8a6a10')
    # Coin piles
    for px, py in [(cx, cy), (margin + wt + 120, cy + 50), (width - margin - wt - 120, cy + 50)]:
        for _ in range(8):
            ox = px + random.randint(-20, 20)
            oy = py + random.randint(-15, 15)
            draw.ellipse([ox - 6, oy - 4, ox + 6, oy + 4], fill=gold, outline='#8a6a10', width=1)


def _interior_generic(draw, description, margin, width, height, color, theme):
    """Default: corner pillars + description-based props."""
    cx, cy = width // 2, height // 2
    wt = 40
    # Corner pillars
    for px, py in [
        (margin + wt, margin + wt),
        (width - margin - wt, margin + wt),
        (margin + wt, height - margin - wt),
        (width - margin - wt, height - margin - wt),
    ]:
        _draw_pillar(draw, px, py, 14, color)
    # Description-based props
    props = []
    if any(k in description for k in ['crate', 'box', 'storage']):
        props.append('crates')
    if 'table' in description or 'desk' in description:
        props.append('table')
    if any(k in description for k in ['chest', 'treasure']):
        props.append('chest')
    if 'barrel' in description:
        props.append('barrels')
    if any(k in description for k in ['torch', 'fire', 'brazier', 'sconce']):
        props.append('torches')
    if not props:
        props = ['barrels', 'crates']
    if 'crates' in props:
        for i in range(2):
            ox = margin + wt + 50 + i * (width - 2 * margin - 2 * wt - 100)
            oy = margin + wt + 50
            draw.rectangle([ox, oy, ox + 42, oy + 42], fill=color, outline='#3a3a3a', width=2)
            draw.line([ox, oy, ox + 42, oy + 42], fill='#3a3a3a', width=1)
            draw.line([ox + 42, oy, ox, oy + 42], fill='#3a3a3a', width=1)
    if 'table' in props:
        draw.rectangle([cx - 50, cy - 25, cx + 50, cy + 25], fill=color, outline='#3a3a3a', width=2)
    if 'chest' in props:
        chx, chy = margin + wt + 50, height - margin - wt - 60
        draw.rectangle([chx, chy + 12, chx + 48, chy + 38], fill='#8B5a1a', outline='#5a3a0a', width=2)
        draw.rectangle([chx, chy, chx + 48, chy + 15], fill='#9B6a2a', outline='#5a3a0a', width=2)
        draw.rectangle([chx + 18, chy + 8, chx + 30, chy + 20], fill='#ccaa33', outline='#8a6a10', width=2)
    if 'barrels' in props:
        for bi in range(3):
            bx = width - margin - wt - 55
            by = margin + wt + 50 + bi * 55
            draw.ellipse([bx, by, bx + 38, by + 38], fill='#5a3a1a', outline='#3a2a0a', width=2)
            draw.line([bx, by + 19, bx + 38, by + 19], fill='#3a2a0a', width=2)
    if 'torches' in props:
        for tx, ty in [(margin + wt + 5, cy - 60), (margin + wt + 5, cy + 60),
                       (width - margin - wt - 5, cy - 60), (width - margin - wt - 5, cy + 60)]:
            draw.rectangle([tx - 4, ty - 18, tx + 4, ty + 18], fill='#6a5a4a', outline='#3a2a1a')
            draw.polygon([(tx, ty - 24), (tx - 7, ty - 18), (tx + 7, ty - 18)], fill='#ff8800', outline='#ff6600')


def _draw_identity_interior(draw, interior_type, identity_lower, description,
                             margin, width, height, furniture_color, theme_lower):
    """Dispatch to the correct interior layout function."""
    funcs = {
        'library': _interior_library,
        'crypt': _interior_crypt,
        'chapel': _interior_chapel,
        'market': _interior_market,
        'boiler': _interior_boiler,
        'tavern': _interior_tavern,
        'throne': _interior_throne,
        'prison': _interior_prison,
        'laboratory': _interior_laboratory,
        'armory': _interior_armory,
        'server': _interior_server,
        'treasury': _interior_treasury,
    }
    fn = funcs.get(interior_type)
    if fn:
        fn(draw, margin, width, height, furniture_color, theme_lower)
    else:
        _interior_generic(draw, description, margin, width, height, furniture_color, theme_lower)


# ─── Room shape modifiers ─────────────────────────────────────────────────────

def _add_corridor_pillars(draw, room_shape, has_north, has_south, has_east, has_west,
                           margin, width, height, color):
    """Add colonnade pillars for corridor rooms to suggest a narrow passage."""
    if room_shape != 'corridor':
        return
    cx, cy = width // 2, height // 2
    wt = 35
    pillar_r = 13
    ns = has_north or has_south
    ew = has_east or has_west
    if ns and not ew:
        for py in range(margin + wt + 60, height - margin - wt - 60, 120):
            _draw_pillar(draw, cx - 130, py, pillar_r, color)
            _draw_pillar(draw, cx + 130, py, pillar_r, color)
    elif ew and not ns:
        for px in range(margin + wt + 60, width - margin - wt - 60, 120):
            _draw_pillar(draw, px, cy - 100, pillar_r, color)
            _draw_pillar(draw, px, cy + 100, pillar_r, color)


def _add_large_hall_columns(draw, room_shape, margin, width, height, color):
    """Add grand columns along the sides for large hall rooms."""
    if room_shape != 'large_hall':
        return
    wt = 35
    pillar_r = 18
    for py in range(margin + wt + 60, height - margin - wt - 60, 130):
        _draw_pillar(draw, margin + wt + 60, py, pillar_r, color)
        _draw_pillar(draw, width - margin - wt - 60, py, pillar_r, color)


# ─── Main generation function ─────────────────────────────────────────────────

def generate_room_map(room_holder, theme_era="Medieval", userId=None):
    """Generate a detailed top-down D&D style battle map."""
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
    room_items = getattr(current_room, "_items", []) or []

    # Room identity for layout decisions
    room_identity = getattr(current_room, '_room_identity', '') or ''
    identity_lower = room_identity.lower()
    room_shape = _classify_room_shape(identity_lower)
    interior_type = _classify_interior(identity_lower, description)

    # Theme colors
    theme_lower = theme_era.lower()
    if 'cyber' in theme_lower:
        # Cyberpunk: near-black with neon blue tints
        floor_base = '#080e18'
        floor_accent = '#0d1828'
        wall_base = '#04080e'
        wall_accent = '#0a1828'
        furniture_color = '#1a3a52'
    elif 'steam' in theme_lower:
        # Steampunk: dark warm brown with bronze/copper accents
        floor_base = '#2a1a08'
        floor_accent = '#1e1206'
        wall_base = '#1a0e04'
        wall_accent = '#3a2010'
        furniture_color = '#7a5020'
    else:  # Medieval
        # Medieval: grey stone
        floor_base = '#484846'
        floor_accent = '#3a3a38'
        wall_base = '#282826'
        wall_accent = '#363634'
        furniture_color = '#5a5a56'

    # Seed for deterministic room appearance
    random.seed(hash(f"{cur_x}_{cur_y}"))

    tile_size = 20
    margin = 60
    wall_thickness = 25

    # Pre-load neighboring rooms so exit checks are accurate
    if userId is not None:
        for nx, ny in [(cur_x, cur_y + 1), (cur_x, cur_y - 1),
                       (cur_x + 1, cur_y), (cur_x - 1, cur_y)]:
            room_holder.get_room(userId, nx, ny)

    # Build exits map
    cols = room_holder._cols
    rows = room_holder._rows
    exits_map = {
        'north': bool(cur_y + 1 < rows and room_array[cur_y + 1][cur_x] is not None),
        'south': bool(cur_y - 1 >= 0 and room_array[cur_y - 1][cur_x] is not None),
        'east':  bool(cur_x + 1 < cols and room_array[cur_y][cur_x + 1] is not None),
        'west':  bool(cur_x - 1 >= 0 and room_array[cur_y][cur_x - 1] is not None),
    }
    has_north = exits_map['north']
    has_south = exits_map['south']
    has_east  = exits_map['east']
    has_west  = exits_map['west']

    # ── FLOOR ─────────────────────────────────────────────────────────────────
    for y in range(margin, height - margin, tile_size):
        for x in range(margin, width - margin, tile_size):
            shade = random.randint(-12, 12)
            r = min(255, max(0, int(floor_base[1:3], 16) + shade))
            g = min(255, max(0, int(floor_base[3:5], 16) + shade))
            b = min(255, max(0, int(floor_base[5:7], 16) + shade))
            draw.rectangle([x, y, x + tile_size - 1, y + tile_size - 1],
                           fill=f'#{r:02x}{g:02x}{b:02x}', outline=floor_accent, width=1)

    # ── WALLS ─────────────────────────────────────────────────────────────────
    wall_style = _get_wall_style(theme_lower, interior_type)
    _draw_all_walls(draw, wall_style, has_north, has_south, has_east, has_west,
                    margin, width, height, wall_base, wall_accent, furniture_color, wall_thickness)

    # ── INTERIOR FEATURES ─────────────────────────────────────────────────────
    _draw_identity_interior(draw, interior_type, identity_lower, description,
                            margin, width, height, furniture_color, theme_lower)

    # ── ROOM SHAPE MODIFIERS ──────────────────────────────────────────────────
    _add_corridor_pillars(draw, room_shape, has_north, has_south, has_east, has_west,
                          margin, width, height, furniture_color)
    _add_large_hall_columns(draw, room_shape, margin, width, height, furniture_color)

    # ── PLAYER MARKER ─────────────────────────────────────────────────────────
    player_x = width // 2
    player_y = height // 2
    draw.ellipse([player_x - 12, player_y - 12, player_x + 12, player_y + 12],
                 fill='#ff3333', outline='#ffffff', width=3)

    # ── ITEM MARKERS ──────────────────────────────────────────────────────────
    rarity_colors = {
        "Legendary": "#f5a524",
        "Epic": "#c678dd",
        "Rare": "#61afef",
        "Uncommon": "#7eca9c",
        "Common": "#d0d0d0",
    }

    def pick_pos():
        for _ in range(12):
            x = random.randint(margin + 20, width - margin - 20)
            y = random.randint(margin + 20, height - margin - 20)
            if (abs(x - player_x) + abs(y - player_y)) > 80:
                return x, y
        return width // 3, height // 3

    for item in room_items:
        name = item.get("name") if isinstance(item, dict) else str(item)
        rarity = (item.get("rarity") if isinstance(item, dict) else "Common") or "Common"
        c = rarity_colors.get(rarity, "#d0d0d0")
        ix, iy = pick_pos()
        draw.ellipse([ix - 8, iy - 8, ix + 8, iy + 8], fill=c, outline="#000000", width=2)
        draw.ellipse([ix - 2, iy - 2, ix + 2, iy + 2], fill="#000000")

    # ── ENCODE ────────────────────────────────────────────────────────────────
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    img_str = base64.b64encode(buffer.getvalue()).decode()
    style = 'border:2px solid #444; border-radius:8px;'
    return f'<img src="data:image/png;base64,{img_str}" style="{style}"/>'


# ─── Legacy helpers (kept for compatibility) ──────────────────────────────────

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
    x1, y1 = px - pw // 2, py - ph // 2
    x2, y2 = px + pw // 2, py + ph // 2
    if t in ('table', 'desk', 'altar', 'console', 'panel'):
        draw.rectangle([x1, y1, x2, y2], fill=color, outline='#3a3a3a', width=2)
    elif t in ('crate', 'box'):
        draw.rectangle([x1, y1, x2, y2], fill=color, outline='#000000', width=2)
        draw.line([x1, y1, x2, y2], fill='#000000', width=1)
        draw.line([x1, y2, x2, y1], fill='#000000', width=1)
    elif t == 'barrel':
        draw.ellipse([x1, y1, x2, y2], fill=color, outline='#3a3a3a', width=2)
    elif t in ('bookcase', 'shelf'):
        draw.rectangle([x1, y1, x2, y2], fill=color, outline='#3a3a3a', width=2)
        for i in range(1, 3):
            yl = y1 + i * (ph // 3)
            draw.line([x1 + 3, yl, x2 - 3, yl], fill='#2a2a2a', width=1)
    elif t in ('server', 'mainframe'):
        draw.rectangle([x1, y1, x2, y2], fill='#1a1a1a', outline='#00ffcc', width=2)
        for i in range(3):
            lx = x1 + 6
            ly = y1 + 6 + i * (ph // 3)
            draw.ellipse([lx, ly, lx + 6, ly + 6], fill='#00ffcc')
    elif t in ('boiler', 'gear', 'pipe'):
        draw.ellipse([x1, y1, x2, y2], fill=color, outline='#3a3a3a', width=2)
    else:
        draw.rectangle([x1, y1, x2, y2], fill=color, outline='#3a3a3a', width=1)


def add_tavern_furniture(draw, margin, width, height, color):
    """Legacy: add tavern-style furniture."""
    _interior_tavern(draw, margin, width, height, color, 'medieval')


def add_library_furniture(draw, margin, width, height, color):
    """Legacy: add library-style furniture."""
    _interior_library(draw, margin, width, height, color, 'medieval')


def add_room_furniture(draw, description, margin, width, height, color, theme):
    """Legacy: add furniture based on room description."""
    _interior_generic(draw, description, margin, width, height, color, theme)

