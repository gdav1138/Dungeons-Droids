from room import room_holder
import random
random.seed(42)

rh = room_holder()
rh.configure_grid(5, 7)
coords = rh.generate_random_connected_room_coords(6, 12, 2, 2)

print("\n=== PLACEMENT DEBUG ===\n")

# Place all rooms
placed = []
for i, (x, y) in enumerate(sorted(coords)):
    identity = f'R{i}'
    rh.add_empty_room(x, y, identity)
    placed.append((x, y, identity))

# Now check what's in the grid
print('Grid contents at [row][col] (row 4=north, row 0=south):')
for row_idx in range(rh._rows - 1, -1, -1):
    print(f'Row {row_idx}: ', end='')
    for col_idx in range(rh._cols):
        r = rh._array_of_rooms[row_idx][col_idx]
        if r is None:
            print('    .', end=' ')
        else:
            ident = getattr(r, "_room_identity", "?")
            print(f'{ident:>4}', end=' ')
    print()

print('\nExpected coords placed:')
for x, y, ident in placed:
    print(f'  {ident} at ({x},{y})')

print('\nNow checking for orphaned/misplaced rooms...')
for x, y, ident in placed:
    actual = rh._array_of_rooms[y][x]
    if actual is None:
        print(f'ERROR: {ident} expected at [{y}][{x}] but found NONE')
    else:
        actual_ident = getattr(actual, "_room_identity", "?")
        if actual_ident != ident:
            print(f'MISMATCH: {ident} expected at [{y}][{x}] but found {actual_ident}')
    
print('\nDone.')
