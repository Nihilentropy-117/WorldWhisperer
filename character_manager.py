"""
Character Location Manager for Pathfinder/D&D campaigns.
Tracks character locations across game sessions and generates narrative reasons.
"""

import os
import json
import random
import difflib
from openrouter_client import get_client


def get_obsidian_paths():
    """Get configured Obsidian vault paths from environment."""
    places = os.getenv('obsidian_places_path', '/home/nihil/Obsidian/TTRPG/Molderia/Places')
    people = os.getenv('obsidian_people_path', '/home/nihil/Obsidian/TTRPG/Molderia/People')
    return places, people


def get_all_characters():
    """Read all character files and return a dict of character names and their content."""
    _, people_path = get_obsidian_paths()

    if not os.path.exists(people_path):
        print(f"Warning: Characters directory not found: {people_path}")
        print("Please configure obsidian_people_path in .env")
        return {}

    characters = {}
    for filename in os.listdir(people_path):
        if filename.endswith('.md'):
            char_name = filename[:-3]  # Remove .md extension
            with open(os.path.join(people_path, filename), 'r', encoding='utf-8') as f:
                characters[char_name] = f.read()
    return characters


def get_all_places():
    """Read all place files and return a dict of place names and their content."""
    places_path, _ = get_obsidian_paths()

    if not os.path.exists(places_path):
        print(f"Warning: Places directory not found: {places_path}")
        print("Please configure obsidian_places_path in .env")
        return {}

    places_dict = {}
    for filename in os.listdir(places_path):
        if filename.endswith('.md'):
            place_name = filename[:-3]  # Remove .md extension
            with open(os.path.join(places_path, filename), 'r', encoding='utf-8') as f:
                places_dict[place_name] = f.read()
    return places_dict


def load_existing_locations(session_num):
    """
    Load existing character locations from session file if it exists.

    Args:
        session_num: Session number

    Returns:
        Dict mapping character names to their current locations
    """
    filename = f"Locations_Session{session_num}.jsonl"
    locations = {}
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data = json.loads(line.strip())
                    locations[data['character']] = data['new_location']
    return locations


def save_location_entry(session_num, character, old_location, new_location, reason):
    """
    Save a location entry to the session JSONL file.

    Args:
        session_num: Session number
        character: Character name
        old_location: Previous location
        new_location: New location
        reason: Narrative reason for the move
    """
    filename = f"Locations_Session{session_num}.jsonl"
    entry = {
        "character": character,
        "old_location": old_location,
        "new_location": new_location,
        "reason_for_location": reason
    }
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry) + '\n')


def call_llm_for_reason(character_name, character_content, place_name, place_content, old_location):
    """
    Call OpenRouter to generate a narrative reason for character being in location.

    Args:
        character_name: Name of the character
        character_content: Character description/stats
        place_name: Name of the place
        place_content: Place description
        old_location: Previous location (optional)

    Returns:
        String describing why the character is at this location
    """
    prompt = f"""Generate a short, creative reason (1-2 sentences) for why this Pathfinder 1e/D&D character is in this location.
Reasons should be personal motivations, not huge plot points.

Character: {character_name}
Character Details:
{character_content[:500]}  # Limit to avoid token bloat

Location: {place_name}
Location Details:
{place_content[:500]}  # Limit to avoid token bloat

Previous Location: {old_location if old_location else 'Unknown'}

Provide only the reason, no additional text."""

    try:
        client = get_client()

        # Use a fast, cheap model for this simple task
        model = os.getenv('character_manager_model', 'google/gemini-2.0-flash-exp:free')

        reason = client.simple_prompt(
            prompt=prompt,
            model=model,
            temperature=0.8
        )

        return reason.strip()

    except Exception as e:
        print(f"Warning: AI generation failed ({e}), using fallback reason")
        return f"Decided to visit {place_name} for personal reasons."


def move_characters():
    """Move all characters to random locations and generate reasons."""
    print("\n" + "="*60)
    print("MOVE CHARACTERS TO RANDOM LOCATIONS")
    print("="*60)

    session_num = input("\nEnter session number: ").strip()
    if not session_num:
        print("Session number is required.")
        return

    print("\nLoading characters and places...")
    characters = get_all_characters()
    places_dict = get_all_places()
    existing_locations = load_existing_locations(session_num)

    if not characters:
        print("❌ No characters found!")
        return
    if not places_dict:
        print("❌ No places found!")
        return

    place_names = list(places_dict.keys())

    print(f"\nMoving {len(characters)} characters for session {session_num}...")
    print("-" * 60)

    for char_name, char_content in characters.items():
        old_location = existing_locations.get(char_name)
        new_location = random.choice(place_names)

        print(f"\n{char_name}:")
        print(f"  Old location: {old_location or 'Unknown'}")
        print(f"  New location: {new_location}")

        # Generate reason using LLM
        reason = call_llm_for_reason(
            char_name, char_content,
            new_location, places_dict[new_location],
            old_location
        )

        # Save to JSONL file
        save_location_entry(session_num, char_name, old_location, new_location, reason)
        print(f"  Reason: {reason}")

    print(f"\n✓ Character movements saved to Locations_Session{session_num}.jsonl")


def fuzzy_search():
    """Search for characters or locations using fuzzy matching."""
    print("\n" + "="*60)
    print("SEARCH CHARACTERS AND LOCATIONS")
    print("="*60)

    search_term = input("\nEnter search term: ").strip()
    if not search_term:
        print("Search term is required.")
        return

    # Get all characters and places
    characters = get_all_characters()
    places_dict = get_all_places()

    # Combine all names for searching
    all_names = list(characters.keys()) + list(places_dict.keys())

    # Use difflib for fuzzy matching
    matches = difflib.get_close_matches(search_term, all_names, n=5, cutoff=0.3)

    if not matches:
        print(f"\n❌ No matches found for '{search_term}'")
        return

    print(f"\n✓ Matches for '{search_term}':")
    print("-" * 60)

    for i, match in enumerate(matches, 1):
        if match in characters:
            print(f"{i}. {match} (Character)")
        else:
            print(f"{i}. {match} (Place)")


def list_locations():
    """List all characters and their locations for a session."""
    print("\n" + "="*60)
    print("LIST CHARACTER LOCATIONS")
    print("="*60)

    print("\nSort by:")
    print("1. Characters and their locations")
    print("2. Locations and their characters")

    choice = input("\nEnter choice (1 or 2): ").strip()
    if choice not in ['1', '2']:
        print("Invalid choice.")
        return

    session_num = input("Enter session number: ").strip()
    if not session_num:
        print("Session number is required.")
        return

    filename = f"Locations_Session{session_num}.jsonl"
    if not os.path.exists(filename):
        print(f"\n❌ No data found for session {session_num}")
        return

    # Load all location data
    locations = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line.strip())
                locations[data['character']] = data['new_location']

    if choice == '1':
        print(f"\n{'Character':<30} → Location")
        print("-" * 60)
        for character in sorted(locations.keys()):
            print(f"{character:<30} → {locations[character]}")

    else:  # choice == '2'
        # Group by location
        location_groups = {}
        for character, location in locations.items():
            if location not in location_groups:
                location_groups[location] = []
            location_groups[location].append(character)

        print(f"\nLocations and Characters (Session {session_num}):")
        print("-" * 60)

        for location in sorted(location_groups.keys()):
            characters_list = ", ".join(sorted(location_groups[location]))
            print(f"\n{location}:")
            print(f"  {characters_list}")


def character_manager_menu():
    """Main menu for character location manager."""
    while True:
        print("\n" + "="*60)
        print("CHARACTER LOCATION MANAGER")
        print("="*60)
        print("1. Move characters to random locations")
        print("2. Search for character or location")
        print("3. List character locations by session")
        print("4. Back to Main Menu")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == '1':
            move_characters()
        elif choice == '2':
            fuzzy_search()
        elif choice == '3':
            list_locations()
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


# For standalone testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    character_manager_menu()