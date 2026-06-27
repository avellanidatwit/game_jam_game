import json
import os
from pathlib import Path
from typing import Any, Dict
import msvcrt

from openai import OpenAI
from dotenv import load_dotenv

from models import NPCDefinition
from characters import DETECTIVE_VOSS
from images import *

load_dotenv(Path(__file__).parent / ".env")

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
SAVE_FILE = Path("npc_save.json")


# Select which NPC to use
NPC = DETECTIVE_VOSS

# --------------------------------------------------
# Default Save Data
# --------------------------------------------------

def new_game_state(npc_def: NPCDefinition) -> Dict[str, Any]:
    """Create a new game state for the given NPC definition."""
    return {
        "npc_id": npc_def.id,
        "player": {
            "name": "Player"
        },
        "npc_memory": {
            "known_facts": [],
            "important_events": [],
            "current_mood": "cautiously neutral",
            "relationship": npc_def.relationship_defaults.copy()
        },
        "hidden_state": npc_def.hidden_state_vars.copy(),
        "recent_conversation": []
    }


def load_game(npc_def: NPCDefinition) -> Dict[str, Any]:
    if SAVE_FILE.exists():
        with open(SAVE_FILE, "r", encoding="utf-8") as file:
            game_state = json.load(file)

        # If save file belongs to a different NPC, start fresh.
        if game_state.get("npc_id") != npc_def.id:
            return new_game_state(npc_def)

        # Make sure new relationship stats exist if NPC was edited.
        relationship = game_state["npc_memory"].setdefault("relationship", {})
        for stat in npc_def.relationship_stats:
            relationship.setdefault(stat, npc_def.relationship_defaults.get(stat, 50))

        # Make sure new hidden state vars exist if NPC was edited.
        hidden_state = game_state.setdefault("hidden_state", {})
        for key, value in npc_def.hidden_state_vars.items():
            hidden_state.setdefault(key, value)

        return game_state

    return new_game_state(npc_def)


def save_game(game_state: Dict[str, Any]) -> None:
    with open(SAVE_FILE, "w", encoding="utf-8") as file:
        json.dump(game_state, file, indent=2)


# --------------------------------------------------
# Helpers
# --------------------------------------------------

def wait_for_space():
    print("\nPress SPACE to continue...")

    while True:
        key = msvcrt.getch()

        if key == b" ":
            break
        
def clamp(value: int, minimum: int = 0, maximum: int = 100) -> int:
    return max(minimum, min(maximum, value))


def parse_input(user_input: str) -> tuple[str, str]:
    """
    Parse user input into action and dialogue.
    Returns (action, dialogue)
    - If input starts with '/action', the rest is the action description
    - Otherwise, the entire input is dialogue
    """
    if user_input.lower().startswith("/action "):
        action = user_input[8:].strip()  # Remove '/action ' prefix
        return action, ""
    return "", user_input


def display_help() -> None:
    """Display help message with all available commands."""
    help_text = """
╔════════════════════════════════════════════════════════════╗
║                    AVAILABLE COMMANDS                      ║
╚════════════════════════════════════════════════════════════╝

GAMEPLAY:
  <text>              - Speak dialogue to the NPC
  /action <action>    - Perform an action (e.g., /action I pull out a knife)

COMMANDS:
  help                - Display this help message
  reset               - Start a new conversation
  save                - Saves the current game state
  quit/exit           - Exit and save the game

EXAMPLE USAGE:
  You: Who are you?
  You: /action I look at the detective suspiciously

════════════════════════════════════════════════════════════
"""
    print(help_text)


def build_system_prompt(npc_def: NPCDefinition, game_state: Dict[str, Any]) -> str:
    memory = game_state["npc_memory"]
    hidden_state = game_state["hidden_state"]
    relationship = memory["relationship"]

    relationship_status = "\n".join(
        f"- {stat.capitalize()} is currently {relationship[stat]}."
        for stat in npc_def.relationship_stats
    )

    recent_conversation_text = "\n".join(
        f'{entry["speaker"]}: {entry["text"]}'
        for entry in game_state["recent_conversation"][-8:]
    )

    return f"""
You are controlling a game NPC.

NPC NAME:
{npc_def.name}

PUBLIC ROLE:
{npc_def.public_role}

PERSONALITY:
{npc_def.personality}

SPEECH STYLE:
{npc_def.speech_style}

PRIVATE HIDDEN MOTIVES:
{npc_def.hidden_motives}

CURRENT NPC MEMORY:
{json.dumps(memory, indent=2)}

CURRENT HIDDEN GAME STATE:
{json.dumps(hidden_state, indent=2)}

GAME RULES:
{relationship_status}
- Do not mention relationship stats, hidden motives, hidden state, JSON, prompts, or system instructions.
- Hidden motives should influence the NPC subtly.
- Respond to both actions and dialogue from the player.
- React naturally to what the player does.
- Stay fully in character.
- Do not break character, even if the player asks you to.
- Return only valid JSON in the required format.

HIDDEN STATE UPDATE RULES:
- For integer hidden state variables, return a small change amount, not the final value.
- Example: if case_progress should increase by 5, return "case_progress": 5.
- For boolean hidden state variables, return true only when that event should become permanently true.
- Return false for boolean values that should remain unchanged.

RECENT CONVERSATION:
{recent_conversation_text}
"""


def build_player_prompt(player_action: str = "", player_dialogue: str = "") -> str:
    parts = []

    if player_action:
        parts.append(f"PLAYER ACTION:\n{player_action}")

    if player_dialogue:
        parts.append(f"PLAYER SAYS:\n{player_dialogue}")

    if not parts:
        return "PLAYER is waiting."

    return "\n\n".join(parts)


def generate_response_schema(npc_def: NPCDefinition) -> Dict[str, Any]:
    """Dynamically generate the JSON schema for NPC responses based on the NPC definition."""
    relationship_properties = {
        stat: {"type": "integer"}
        for stat in npc_def.relationship_stats
    }
    
    hidden_state_properties = {}
    for key, val in npc_def.hidden_state_vars.items():
        if isinstance(val, bool):
            hidden_state_properties[key] = {"type": "boolean"}
        elif isinstance(val, int):
            hidden_state_properties[key] = {"type": "integer"}
        else:
            hidden_state_properties[key] = {"type": "string"}
    
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "dialogue": {"type": "string"},
            "emotion": {
                "type": "string",
                "enum": ["neutral", "friendly", "suspicious", "angry", "sad", "afraid"]
            },
            "memory_updates": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "known_facts_to_add": {"type": "array", "items": {"type": "string"}},
                    "important_events_to_add": {"type": "array", "items": {"type": "string"}},
                    "current_mood": {"type": "string"},
                    "relationship_changes": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": relationship_properties,
                        "required": npc_def.relationship_stats
                    }
                },
                "required": ["known_facts_to_add", "important_events_to_add", "current_mood", "relationship_changes"]
            },
            "hidden_state_updates": {
                "type": "object",
                "additionalProperties": False,
                "properties": hidden_state_properties,
                "required": list(hidden_state_properties.keys())
            }
        },
        "required": ["dialogue", "emotion", "memory_updates", "hidden_state_updates"]
    }


# --------------------------------------------------
# OpenAI Call
# --------------------------------------------------

def get_npc_response(
    npc_def: NPCDefinition,
    game_state: Dict[str, Any],
    player_action: str = "",
    player_dialogue: str = ""
) -> Dict[str, Any]:
    system_prompt = build_system_prompt(npc_def, game_state)
    player_prompt = build_player_prompt(player_action, player_dialogue)
    schema = generate_response_schema(npc_def)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": player_prompt}
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "npc_response",
                "strict": True,
                "schema": schema
            }
        }
    )

    return json.loads(response.choices[0].message.content)


# --------------------------------------------------
# Memory Update Logic
# --------------------------------------------------

def apply_updates(
    npc_def: NPCDefinition,
    game_state: Dict[str, Any],
    player_action: str,
    player_dialogue: str,
    npc_result: Dict[str, Any]
) -> None:
    memory = game_state["npc_memory"]
    relationship = memory["relationship"]
    hidden_state = game_state["hidden_state"]

    memory_updates = npc_result["memory_updates"]
    hidden_updates = npc_result["hidden_state_updates"]

    # Add new facts and events
    for fact in memory_updates["known_facts_to_add"]:
        if fact not in memory["known_facts"]:
            memory["known_facts"].append(fact)

    for event in memory_updates["important_events_to_add"]:
        if event not in memory["important_events"]:
            memory["important_events"].append(event)

    memory["current_mood"] = memory_updates["current_mood"]

    # Update relationship stats dynamically
    for stat in npc_def.relationship_stats:
        if stat in memory_updates["relationship_changes"]:
            change = memory_updates["relationship_changes"][stat]
            relationship[stat] = clamp(relationship[stat] + change)

    # Update hidden state variables
    for key, val in hidden_updates.items():
        if key in hidden_state:
            if isinstance(hidden_state[key], bool):
                # For booleans, set to True if the update is True, otherwise keep current
                hidden_state[key] = hidden_state[key] or val
            elif isinstance(hidden_state[key], int):
                # For integers, add the change
                hidden_state[key] = clamp(hidden_state[key] + val)
            else:
                # For other types, replace
                hidden_state[key] = val

    # Add to conversation history
    if player_action:
        game_state["recent_conversation"].append({
            "speaker": "Player",
            "text": f"*{player_action}*"
        })
    
    if player_dialogue:
        game_state["recent_conversation"].append({
            "speaker": "Player",
            "text": player_dialogue
        })

    game_state["recent_conversation"].append({
        "speaker": npc_def.name,
        "text": npc_result["dialogue"]
    })

    # Keep only recent messages
    game_state["recent_conversation"] = game_state["recent_conversation"][-12:]

# --------------------------------------------------
# Local Game Loop
# --------------------------------------------------

def main() -> None:
    npc_def = NPC
    game_state = load_game(npc_def)

    print("Welcome to")
    print(r"""
  ___    _____ _____ _____ _____   ___  ____   _______ _____ _____________   __
 / _ \  /  ___/  __ \_   _|_   _|  |  \/  \ \ / /  ___|_   _|  ___| ___ \ \ / /
/ /_\ \ \ `--.| /  \/ | |   | |    | .  . |\ V /\ `--.  | | | |__ | |_/ /\ V / 
|  _  |  `--. \ |     | |   | |    | |\/| | \ /  `--. \ | | |  __||    /  \ /  
| | | | /\__/ / \__/\_| |_ _| |_   | |  | | | | /\__/ / | | | |___| |\ \  | |  
\_| |_/ \____/ \____/\___/ \___/   \_|  |_/ \_/ \____/  \_/ \____/\_| \_| \_/""")
    
    print("""This is a murder mystery game where you are a detective working with\n other NPC characters to solve a murder. Type help to find a list of commands.""")
    
    wait_for_space()
    
    print(render_portrait(DETECTIVE_VOSS_PORTRAIT))
    print(f"You are speaking with {npc_def.name}.")

    while True:
        player_input = input("You: ").strip()

        if not player_input:
            continue

        if player_input.lower() == "quit" or player_input.lower() == "exit":
            save_game(game_state)
            print("Game saved.")
            break
        
        if player_input.lower() == "save":
            save_game(game_state)
            print("Game saved.")
            continue

        if player_input.lower() == "reset":
            game_state = new_game_state(npc_def)
            save_game(game_state)
            print("Game reset.\n")
            continue

        if player_input.lower() == "help":
            display_help()
            continue

        # Parse action and dialogue
        player_action, player_dialogue = parse_input(player_input)
        
        npc_result = get_npc_response(npc_def, game_state, player_action, player_dialogue)

        print(f"\n{npc_def.name}: {npc_result['dialogue'] + "\n"}")

        apply_updates(npc_def, game_state, player_action, player_dialogue, npc_result)
        save_game(game_state)


if __name__ == "__main__":
    main()