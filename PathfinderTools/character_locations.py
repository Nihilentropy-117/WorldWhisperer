#!/usr/bin/env python3
import os
import json
import random
import subprocess
import difflib

places = "/home/nihil/Obsidian/TTRPG/Molderia/Places"
people = "/home/nihil/Obsidian/TTRPG/Molderia/People"

def get_all_characters():
    """Read all character files and return a list of character names and their file contents."""
    characters = {}
    for filename in os.listdir(people):
        if filename.endswith('.md'):
            char_name = filename[:-3]  # Remove .md extension
            with open(os.path.join(people, filename), 'r', encoding='utf-8') as f:
                characters[char_name] = f.read()
    return characters

def get_all_places():
    """Read all place files and return a list of place names and their file contents."""
    places_dict = {}
    for filename in os.listdir(places):
        if filename.endswith('.md'):
            place_name = filename[:-3]  # Remove .md extension
            with open(os.path.join(places, filename), 'r', encoding='utf-8') as f:
                places_dict[place_name] = f.read()
    return places_dict

def load_existing_locations(session_num):
    """Load existing character locations from session file if it exists."""
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
    """Save a location entry to the session JSONL file."""
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
    """Call OpenRouter LLM to generate a reason for character being in location."""
    prompt = f"""Generate a short, creative reason (1-2 sentences) for why this Pathfinder 1e character is in this location. 
    Reasons should not be huge plot points, just personal reasons.

Character: {character_name}
Character Details:
{character_content}

Location: {place_name}
Location Details:
{place_content}

Previous Location: {old_location if old_location else 'Unknown'}

Provide only the reason, no additional text."""

    # Create the curl command for OpenRouter
    curl_data = {
        "model": "google/gemini-2.5-flash-lite",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        # Use curl to call OpenRouter API
        result = subprocess.run([
            'curl', '-s', '-X', 'POST',
            'https://openrouter.ai/api/v1/chat/completions',
            '-H', 'Content-Type: application/json',
            '-H', f'Authorization: Bearer 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',
            '-d', json.dumps(curl_data)
        ], capture_output=True, text=True)

        if result.returncode == 0:
            response = json.loads(result.stdout)
            if 'choices' in response and len(response['choices']) > 0:
                return response['choices'][0]['message']['content'].strip()
            else:
                print(response)
                pass

        return f"Decided to visit {place_name} for personal reasons."
    except Exception as e:
        return f"Found themselves in {place_name} through circumstances."

def move_characters():
    """Implement option 1: Move characters to random locations."""
    session_num = input("Enter session number: ").strip()
    if not session_num:
        print("Session number is required.")
        return

    print("Loading characters and places...")
    characters = get_all_characters()
    places_dict = get_all_places()
    existing_locations = load_existing_locations(session_num)

    if not characters:
        print("No characters found!")
        return
    if not places_dict:
        print("No places found!")
        return

    place_names = list(places_dict.keys())

    print(f"\nMoving {len(characters)} characters for session {session_num}...")

    for char_name, char_content in characters.items():
        old_location = existing_locations.get(char_name)
        new_location = random.choice(place_names)

        print(f"Moving {char_name} to {new_location}...")

        # Generate reason using LLM
        reason = call_llm_for_reason(
            char_name, char_content,
            new_location, places_dict[new_location],
            old_location
        )

        # Save to JSONL file
        save_location_entry(session_num, char_name, old_location, new_location, reason)
        print(f"  Reason: {reason}")

    print(f"\nCharacter movements saved to Locations_Session{session_num}.jsonl")

def fuzzy_search():
    """Implement option 2: Search for character or location."""
    search_term = input("Enter search term: ").strip()
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
        print("No matches found.")
        return

    print(f"\nMatches for '{search_term}':")
    for i, match in enumerate(matches, 1):
        if match in characters:
            print(f"{i}. {match} (Character)")
        else:
            print(f"{i}. {match} (Place)")

def list_locations():
    """Implement option 3: List all characters and their locations."""
    print("Sort by:")
    print("1. Characters and their locations")
    print("2. Locations and their characters")

    choice = input("Enter choice (1 or 2): ").strip()
    if choice not in ['1', '2']:
        print("Invalid choice.")
        return

    session_num = input("Enter session number: ").strip()
    if not session_num:
        print("Session number is required.")
        return

    filename = f"Locations_Session{session_num}.jsonl"
    if not os.path.exists(filename):
        print(f"No data found for session {session_num}.")
        return

    # Load all location data
    locations = {}
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                data = json.loads(line.strip())
                locations[data['character']] = data['new_location']

    if choice == '1':
        print(f"\nCharacters and their locations (Session {session_num}):")
        print("-" * 50)
        for character in sorted(locations.keys()):
            print(f"{character:30} -> {locations[character]}")

    else:  # choice == '2'
        # Group by location
        location_groups = {}
        for character, location in locations.items():
            if location not in location_groups:
                location_groups[location] = []
            location_groups[location].append(character)

        print(f"\nLocations and their characters (Session {session_num}):")
        print("-" * 50)
        for location in sorted(location_groups.keys()):
            characters_list = ", ".join(sorted(location_groups[location]))
            print(f"{location}:")
            print(f"  {characters_list}")
            print()

def main():
    """Main program loop."""
    while True:
        print("\n" + "="*50)
        print("CHARACTER LOCATIONS MANAGER")
        print("="*50)
        print("1. Move characters")
        print("2. Search for character or location")
        print("3. List all characters and their locations")
        print("4. Exit")

        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == '1':
            move_characters()
        elif choice == '2':
            fuzzy_search()
        elif choice == '3':
            list_locations()
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main()