import json
from typing import Any, Dict
from open_ai_api import call_ai

SCHEMA_EXAMPLE = {
  "room_type": "alley",  # one of: alley|corridor|chamber|tavern|library|lab|street|temple
  "floor": {
    "material": "cobbles",  # stone|wood|metal|concrete|cobbles|tile|marble
    "base": "#4a4a4a",
    "accent": "#2e2e2e",
    "pattern": "cobbles"  # grid|herringbone|hex|cobbles|plates
  },
  "zones": [
    {"shape":"rect", "x":0.1, "y":0.1, "w":0.8, "h":0.8, "role":"room"}
  ],
  "walls": [
    {"edge":"north", "open": False}, {"edge":"south","open": True}, {"edge":"east","open": False}, {"edge":"west","open": True}
  ],
  "props": [
    {"type":"table", "x":0.5, "y":0.6, "w":0.12, "h":0.08, "rotation":0}
  ]
}

SYSTEM_PROMPT = (
    "You are a dungeon battle-map layout planner.\n"
    "Given a short room description TEXT, the THEME era, and which edges have EXITS,\n"
    "produce a compact JSON object following the exact SCHEMA.\n"
    "Rules:\n"
    "- Return ONLY minified JSON (no markdown, no comments).\n"
    "- room_type must be one of: alley|corridor|chamber|tavern|library|lab|street|temple.\n"
    "- Choose floor colors/materials to match TEXT and THEME (hex colors).\n"
    "- Use 1 rectangle in zones for the main walkable area (role=room or path).\n"
    "- walls: include 4 edges with open true/false according to EXITS.\n"
    "- props: 5 to 10 items, types appropriate to THEME and TEXT (e.g., crates/barrels/tables for fantasy; console/server/neon for cyberpunk; boiler/pipe/gear for steampunk).\n"
    "- Each prop x,y is normalized within the interior 0..1 (avoid 0.45..0.55 if center should be clear).\n"
)


def _build_prompt(text: str, theme: str, exits: Dict[str, bool]) -> str:
    return (
        SYSTEM_PROMPT
        + "\nSCHEMA=" + json.dumps(SCHEMA_EXAMPLE)
        + "\nTHEME=" + theme
        + "\nEXITS=" + json.dumps(exits)
        + "\nTEXT=" + text.strip()
        + "\nJSON:"
    )


def get_map_layout(text: str, theme: str, exits: Dict[str, bool]) -> Dict[str, Any]:
    """Return a JSON-like dict describing the layout. Falls back to a simple default if parsing fails."""
    prompt = _build_prompt(text or "", theme or "Unknown", exits or {})
    try:
        raw = call_ai(prompt)
        # Try to extract JSON
        raw = raw.strip()
        # If wrapped in code fences, remove them
        if raw.startswith("```") and raw.endswith("```"):
            raw = raw.strip("`\n")
        # Some models may prepend text; find first '{' and last '}'
        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1:
            raw = raw[start:end+1]
        data = json.loads(raw)
        return data
    except Exception:
        # Fallback default layout
        return {
            "room_type": "chamber",
            "floor": {"material": "stone", "base": "#5a4a3a", "accent": "#3a2a1a", "pattern": "grid"},
            "zones": [{"shape":"rect","x":0.08,"y":0.08,"w":0.84,"h":0.84,"role":"room"}],
            "walls": [
                {"edge":"north","open": bool(exits.get("north"))},
                {"edge":"south","open": bool(exits.get("south"))},
                {"edge":"east","open": bool(exits.get("east"))},
                {"edge":"west","open": bool(exits.get("west"))},
            ],
            "props": [
                {"type":"table","x":0.5,"y":0.6,"w":0.14,"h":0.08,"rotation":0},
                {"type":"crate","x":0.25,"y":0.25,"w":0.08,"h":0.08,"rotation":0},
                {"type":"barrel","x":0.75,"y":0.28,"w":0.08,"h":0.1,"rotation":0},
            ],
        }
