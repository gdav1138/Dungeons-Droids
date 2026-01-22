# Item class for lootable items in the game
import random

class Item:
    def __init__(self, name, description, item_type, value=0):
        self._name = name
        self._description = description
        self._item_type = item_type  # weapon, armor, potion, treasure, etc.
        self._value = value
    
    def get_name(self):
        return self._name
    
    def get_description(self):
        return self._description
    
    def get_type(self):
        return self._item_type
    
    def get_value(self):
        return self._value


def generate_random_item(theme_era):
    """Generate a random item based on the theme"""
    
    # Theme-specific item templates
    item_templates = {
        'medieval': [
            ('Rusty Sword', 'An old but still serviceable blade', 'weapon', 15),
            ('Iron Shield', 'A sturdy shield with a dented surface', 'armor', 20),
            ('Health Potion', 'A small vial of red liquid', 'potion', 10),
            ('Gold Coins', 'A small pouch of gold coins', 'treasure', 25),
            ('Ancient Scroll', 'A yellowed scroll with strange runes', 'treasure', 30),
        ],
        'sci-fi': [
            ('Plasma Pistol', 'A compact energy weapon', 'weapon', 35),
            ('Energy Shield', 'A portable force field generator', 'armor', 40),
            ('Med-Kit', 'Advanced medical supplies', 'potion', 20),
            ('Credits', 'A data chip containing credits', 'treasure', 25),
            ('Tech Module', 'A mysterious piece of technology', 'treasure', 45),
        ],
        'cyberpunk': [
            ('Neural Chip', 'A wetware enhancement chip', 'treasure', 40),
            ('Mono-Knife', 'A monomolecular blade', 'weapon', 30),
            ('Stim Pack', 'Chemical enhancement injector', 'potion', 15),
            ('Eddies', 'Stack of cryptocurrency', 'treasure', 20),
            ('Corporate Keycard', 'High-level access credentials', 'treasure', 35),
        ],
        'steampunk': [
            ('Brass Goggles', 'Protective eyewear with multiple lenses', 'armor', 18),
            ('Steam Wrench', 'A heavy mechanical tool', 'weapon', 22),
            ('Aether Vial', 'Condensed energy in a brass container', 'potion', 25),
            ('Gearwork Trinket', 'An intricate mechanical device', 'treasure', 30),
            ('Copper Cogs', 'Valuable mechanical parts', 'treasure', 15),
        ],
    }
    
    # Default fantasy items if theme not found
    default_items = [
        ('Dagger', 'A sharp blade', 'weapon', 12),
        ('Leather Armor', 'Basic protective gear', 'armor', 15),
        ('Healing Salve', 'Medicinal ointment', 'potion', 10),
        ('Gem', 'A sparkling gemstone', 'treasure', 20),
        ('Old Key', 'A mysterious key', 'treasure', 5),
    ]
    
    # Try to find theme-specific items, fallback to default
    theme_lower = theme_era.lower()
    items_list = default_items
    
    for theme_key in item_templates:
        if theme_key in theme_lower:
            items_list = item_templates[theme_key]
            break
    
    # Select random item
    item_data = random.choice(items_list)
    return Item(item_data[0], item_data[1], item_data[2], item_data[3])
