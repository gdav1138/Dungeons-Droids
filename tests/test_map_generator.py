"""
Tests for Map Generator: generate_room_map output and drawing helpers.
"""
import pytest
from PIL import Image, ImageDraw


class TestGenerateRoomMap:
    """generate_room_map return value and theme handling."""

    def test_returns_img_tag_with_base64(self):
        from map_generator import generate_room_map
        from room import room_holder
        rh = room_holder()
        rh.add_empty_room(0, 0)
        r = rh.get_current_room()
        r._description = "A small chamber"
        r._items = []
        out = generate_room_map(rh, "Medieval")
        assert out.strip().startswith("<img ")
        assert "data:image/png;base64," in out
        assert "src=" in out

    def test_theme_medieval_produces_image(self):
        from map_generator import generate_room_map
        from room import room_holder
        rh = room_holder()
        rh.add_empty_room(0, 0)
        rh.get_current_room()._description = "Dungeon"
        rh.get_current_room()._items = []
        out = generate_room_map(rh, "Medieval")
        assert "data:image/png;base64," in out

    def test_theme_cyberpunk_produces_image(self):
        from map_generator import generate_room_map
        from room import room_holder
        rh = room_holder()
        rh.add_empty_room(0, 0)
        rh.get_current_room()._description = "Server room"
        rh.get_current_room()._items = []
        out = generate_room_map(rh, "cyberpunk")
        assert "data:image/png;base64," in out

    def test_theme_steampunk_produces_image(self):
        from map_generator import generate_room_map
        from room import room_holder
        rh = room_holder()
        rh.add_empty_room(0, 0)
        rh.get_current_room()._description = "Engine room"
        rh.get_current_room()._items = []
        out = generate_room_map(rh, "steampunk")
        assert "data:image/png;base64," in out


class TestMapGeneratorDrawHelpers:
    """Drawing helpers do not crash and produce expected structure."""

    def test_draw_stone_wall(self):
        from map_generator import draw_stone_wall
        img = Image.new("RGB", (200, 200), color="#000")
        draw = ImageDraw.Draw(img)
        draw_stone_wall(draw, 10, 10, 100, 100, "#2a2520", "#3a3530")
        assert True

    def test_draw_door_north_south(self):
        from map_generator import draw_door
        img = Image.new("RGB", (200, 200), color="#000")
        draw = ImageDraw.Draw(img)
        draw_door(draw, 50, 10, 80, 25, "north", "#6a5545")
        draw_door(draw, 50, 150, 80, 25, "south", "#6a5545")
        assert True

    def test_draw_door_east_west(self):
        from map_generator import draw_door
        img = Image.new("RGB", (200, 200), color="#000")
        draw = ImageDraw.Draw(img)
        draw_door(draw, 10, 50, 25, 80, "west", "#6a5545")
        draw_door(draw, 165, 50, 25, 80, "east", "#6a5545")
        assert True

    def test_draw_prop_table(self):
        from map_generator import _draw_prop
        img = Image.new("RGB", (400, 400), color="#000")
        draw = ImageDraw.Draw(img)
        _draw_prop(draw, {"x": 0.5, "y": 0.5, "w": 0.1, "h": 0.1, "type": "table"}, 60, 800, 600, "#6a5545", "medieval")
        assert True

    def test_draw_prop_empty_safe(self):
        from map_generator import _draw_prop
        img = Image.new("RGB", (400, 400), color="#000")
        draw = ImageDraw.Draw(img)
        _draw_prop(draw, {}, 60, 800, 600, "#6a5545", "medieval")
        assert True
