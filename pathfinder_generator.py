"""
Pathfinder 1e Item Generator
Generates Pathfinder 1e items (weapons, armor, NPCs, etc.) using AI.
"""

import os
import random
import re
from datetime import datetime
from openrouter_client import get_client


def roll_dice(dice_expression):
    """
    Roll dice from a string expression (e.g., "2d6+3" or "1d20-2").

    Args:
        dice_expression: String like "2d6+3" or "1d20"

    Returns:
        Integer result of the dice roll
    """
    # Split the expression by operators and keep the operators
    tokens = re.split(r'([+\-*/()])', dice_expression)
    tokens = [t.strip() for t in tokens if t.strip()]

    # Replace dice expressions with their results
    for i, token in enumerate(tokens):
        if 'd' in token:
            num_dice, dice_value = map(int, token.split('d'))
            roll_result = sum(random.randint(1, dice_value) for _ in range(num_dice))
            tokens[i] = str(roll_result)

    # Join the tokens back into a single string and evaluate
    return eval(''.join(tokens))


def dice_roller_interface():
    """Interactive dice roller."""
    print("\n" + "="*60)
    print("DICE ROLLER")
    print("="*60)
    print("Enter dice expressions like: 2d6+3, 1d20, 3d8-2")
    print("Type 'back' to return to menu\n")

    while True:
        dice_expression = input("Enter dice expression (or 'back'): ").strip()

        if dice_expression.lower() == 'back':
            break

        try:
            result = roll_dice(dice_expression)
            print(f"Result: {result}\n")
        except Exception as e:
            print(f"Invalid expression: {e}\n")


def item_generator_menu():
    """Display submenu for item generation."""
    item_types = [
        "Amulet",
        "Ring",
        "Clothes",
        "Magic Weapon",
        "Magic Armor",
        "Wand",
        "Staff",
        "Scroll",
        "Potion",
        "Spell",
        "NPC",
        "Monster",
    ]

    print("\n" + "="*60)
    print("PATHFINDER 1E ITEM GENERATOR")
    print("="*60)

    for i, item_type in enumerate(item_types, 1):
        print(f"{i}. {item_type}")
    print(f"{len(item_types) + 1}. Back to Menu")

    while True:
        try:
            choice = int(input("\nEnter your choice: "))
            if 1 <= choice <= len(item_types):
                selected_type = item_types[choice - 1]

                # Special handling for NPC
                if selected_type == "NPC":
                    print("\nNPC Options:")
                    print("1. Full NPC (stat block + description)")
                    print("2. Description only (no stats)")
                    print("3. Stat block only (no description/feats)")

                    npc_choice = int(input("Enter choice (1-3): "))
                    if npc_choice == 1:
                        selected_type = "NPC with stat block and character description"
                    elif npc_choice == 2:
                        selected_type = "NPC NO STATS, just a brief character description"
                    elif npc_choice == 3:
                        selected_type = "NPC Just a stat block, NO DESCRIPTION OR FEATS/ABILITIES"

                generate_item(selected_type)
                break

            elif choice == len(item_types) + 1:
                break
            else:
                print("Invalid choice. Please try again.")
        except ValueError:
            print("Please enter a valid number.")


def generate_item(item_type):
    """
    Generate a Pathfinder 1e item using OpenRouter.

    Args:
        item_type: Type of item to generate
    """
    print(f"\nGenerating {item_type}...")

    # Get party defaults from environment
    default_level = os.getenv('pathfinder_party_level', '3')
    default_size = os.getenv('pathfinder_party_size', '3')

    # Collect additional information from user
    additional_info = input(f"Enter specific details for this {item_type} (or press Enter to skip): ").strip()

    # Prepare the prompt
    prompt = f"""USER REQUEST: Generate a detailed Pathfinder 1e {item_type}.

REQUIREMENTS:
- Follow official Pathfinder 1e rules and formatting
- Include all necessary game mechanics (stats, bonuses, requirements, etc.) unless specified otherwise
- Provide a detailed description including appearance and lore
- Include appropriate cost and crafting requirements
- Make it balanced for typical gameplay for a group of {default_size}x level {default_level} adventurers
- The Rule of Cool is Law, but don't break the game

Additional requirements: {additional_info if additional_info else 'None specified'}

Format the output as a complete game-ready entry."""

    try:
        client = get_client()

        # Use a more creative model for item generation
        model = os.getenv('pathfinder_generator_model', 'anthropic/claude-3.5-sonnet')

        print("\nCalling AI to generate item...")
        generated_content = client.simple_prompt(
            prompt=prompt,
            model=model,
            temperature=0.9  # Higher creativity for item generation
        )

        print("\n" + "="*60)
        print(f"GENERATED {item_type.upper()}")
        print("="*60)
        print(generated_content)
        print("="*60)

        # Ask if user wants to save
        save_choice = input("\nSave to file? (y/n): ").lower().strip()

        if save_choice in ['y', 'yes']:
            save_location_choice = input("Save to Notes directory for WorldWhisperer indexing? (y/n): ").lower().strip()

            if save_location_choice in ['y', 'yes']:
                save_to_notes(item_type, generated_content, additional_info)
            else:
                save_to_markdown(item_type, generated_content, additional_info)

    except Exception as e:
        print(f"Error generating item: {str(e)}")


def save_to_markdown(item_type, content, additional_info):
    """
    Save generated item to a markdown file in current directory.

    Args:
        item_type: Type of item generated
        content: Generated content
        additional_info: User's additional requirements
    """
    # Create filename
    filename = f"{item_type.lower().replace(' ', '_')}_{random.randint(1000, 9999)}.md"

    # Create markdown content
    markdown_content = f"# {item_type}\n\n"
    if additional_info:
        markdown_content += f"**User Requirements:** {additional_info}\n\n"
    markdown_content += f"**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    markdown_content += "---\n\n"
    markdown_content += content

    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"✓ Saved to: {filename}")
    except Exception as e:
        print(f"Error saving file: {str(e)}")


def save_to_notes(item_type, content, additional_info):
    """
    Save generated item to Notes directory for WorldWhisperer indexing.

    Args:
        item_type: Type of item generated
        content: Generated content
        additional_info: User's additional requirements
    """
    # Determine subdirectory based on item type
    if item_type.lower().startswith('npc'):
        subdir = "Characters"
    elif 'monster' in item_type.lower():
        subdir = "Monsters"
    else:
        subdir = "Items"

    # Create directory path
    notes_dir = "Notes"
    full_dir = os.path.join(notes_dir, subdir)

    # Ensure directory exists
    os.makedirs(full_dir, exist_ok=True)

    # Create filename
    base_name = item_type.lower().replace(' ', '_')
    filename = f"{base_name}_{random.randint(1000, 9999)}.md"
    full_path = os.path.join(full_dir, filename)

    # Create markdown content (simpler format for vectorization)
    markdown_content = f"# {item_type}\n\n"
    if additional_info:
        markdown_content += f"**Requirements:** {additional_info}\n\n"
    markdown_content += content

    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"✓ Saved to Notes: {full_path}")
        print("  → Will be indexed next time you update ChromaDB")
    except Exception as e:
        print(f"Error saving to Notes: {str(e)}")


# For standalone testing
if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    while True:
        print("\n1. Dice Roller")
        print("2. Item Generator")
        print("3. Exit")

        choice = input("Choice: ").strip()

        if choice == '1':
            dice_roller_interface()
        elif choice == '2':
            item_generator_menu()
        elif choice == '3':
            break