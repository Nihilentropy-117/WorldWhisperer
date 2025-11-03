import re
import random
import json

import subprocess
from datetime import datetime

defaults = {"level": "3", "party_size": "3"}
def roll_dice(dice_expression):
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


def menu(options):
    """
    Display a list of options with numbers and let the user choose one.

    Args:
    - options (list): A list of strings representing the options.

    Returns:
    - str: The chosen option.
    """
    # Print the options with numbers
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")

    # Get user's choice
    while True:
        try:
            choice = int(input("Enter the number of your choice: "))
            if 1 <= choice <= len(options):
                return options[choice - 1]
            else:
                print("Invalid choice. Please choose a number from the list.")
        except ValueError:
            print("Please enter a valid number.")


def generator_menu():
    """
    Display the generator submenu for Pathfinder 1e items.
    """
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
        "Back to Main Menu"
    ]

    choice = menu(item_types)

    if choice == "NPC":
        choice +=  menu([" with stat block and character description", " NO STATS, just a brief character description", " Just a stat block, NO DESCRIPTION OR FEATS/ABILITIES"])
    if choice == "Back to Main Menu":
        return

    generate_item(choice)


def generate_item(item_type):
    """
    Generate a Pathfinder 1e item using OpenRouter LLM.
    """
    print(f"\nGenerating {item_type}...")

    # Collect additional information from user
    additional_info = input(f"Enter any specific details you want for this {item_type} (or press Enter to skip): ")

    # Prepare the prompt
    prompt = f"""USER REQUEST: Generate a detailed Pathfinder 1e {item_type}.
REQUIREMENTS::
- Follow official Pathfinder 1e rules and formatting
- Include all necessary game mechanics (stats, bonuses, requirements, etc.) unless the user request specifies otherwise
- Provide a detailed description including appearance and lore
- Include appropriate cost and crafting requirements
- Make it balanced for typical gameplay for a group of {defaults['party_size']}x{defaults['level']}rd level adventurers
- The Rule of Cool is Law, but don't break the game

Additional requirements: {additional_info if additional_info else 'None specified'}

Format the output as a complete game-ready entry."""

    try:
        # Get OpenRouter API key from environment variable
        api_key = "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"

        # Prepare JSON payload
        payload = {
            "model": "openrouter/sonoma-sky-alpha",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        # Call OpenRouter API using curl
        curl_command = [
            'curl',
            '-X', 'POST',
            'https://openrouter.ai/api/v1/chat/completions',
            '-H', 'Content-Type: application/json',
            '-H', f'Authorization: Bearer {api_key}',
            '-d', json.dumps(payload)
        ]

        result = subprocess.run(curl_command, capture_output=True, text=True)

        if result.returncode == 0:
            response_data = json.loads(result.stdout)
            generated_content = response_data['choices'][0]['message']['content']

            print("\n" + "="*60)
            print(f"GENERATED {item_type.upper()}")
            print("="*60)
            print(generated_content)
            print("="*60)

            # Ask if user wants to save
            save_choice = input("\nSave to .md file? (y/n): ").lower().strip()

            if save_choice == 'y' or save_choice == 'yes':
                save_to_markdown(item_type, generated_content, additional_info)

        else:
            print(f"Error calling OpenRouter API: {result.stderr}")

    except Exception as e:
        print(f"Error generating item: {str(e)}")


def save_to_markdown(item_type, content, additional_info):
    """
    Save the generated item to a markdown file.
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
        print(f"Saved to: {filename}")
    except Exception as e:
        print(f"Error saving file: {str(e)}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    i = True
    k = True
    while i is True: ## Main Loop - i = False to exit program
        while k is True: ## Menu Loop - k = False to exit to menu
            choice = menu(["Dice", "Generator", "Quit"])
            if choice == "Dice":

                dice_expression = input("Enter the dice expression: ")
                print(f"Result: {roll_dice(dice_expression)}")

            elif choice == "Generator":
                generator_menu()

            elif choice == "Quit":
                i = False

            else: print("Invalid Choice")