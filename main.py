#!/usr/bin/env python3
"""
WorldWhisperer - Master Program
Integrated D&D/Pathfinder campaign management tool combining:
- World lore management with vector database
- Pathfinder 1e item generation
- Character location tracking
- Shop profit calculator
"""

import os
from dotenv import load_dotenv

# Core modules
import data_code
import llm_code
import chromadb_code

# Pathfinder Tools modules
import pathfinder_generator
import character_manager
import shop_calculator

# Menu system
from menu_system import display_header, get_choice, confirm, pause


def call_pine_gpt(admin_command=None, additional_context=None, prompt=None, mode='question'):
    """
    Query ChromaDB and generate response.

    Args:
        admin_command: System instruction/role
        additional_context: Additional user-provided context
        prompt: User's prompt/question
        mode: 'question' for Q&A, 'generator' for content creation
    """
    # Get context from ChromaDB with mode-specific formatting
    loaded_query, relevance_data = chromadb_code.get_chromadb_context(
        prompt + "\n" + additional_context,
        mode=mode
    )

    # Use enhanced generation for Generator mode
    if mode == 'generator':
        result = gpt_code.generate_with_feedback(
            admin_command,
            loaded_query,
            prompt,
            relevance_data
        )
    else:
        result = gpt_code.llm(admin_command, " ", loaded_query)

    print("\n" + "="*70)
    print(result)
    print("="*70)
    return result


def world_lore_menu():
    """World Lore Manager submenu."""
    while True:
        display_header("WORLD LORE MANAGER", "Main Menu > World Lore")

        options = [
            "Interactive Mode (custom instructions)",
            "Questions Mode (ask about your world)",
            "Generator Mode (create new lore)"
        ]

        idx, choice = get_choice(options)

        if idx is None:  # Back
            break

        if idx == 0:  # Interactive
            print("\n" + "-"*70)
            admin_command = input("System Instruction: ")
            additional_context = input("Additional Context: ")
            prompt = input("Prompt: ")
            call_pine_gpt(admin_command, additional_context, prompt, mode='question')
            pause()

        elif idx == 1:  # Questions
            print("\n" + "-"*70)
            prompt = input("Your Question: ")
            call_pine_gpt(
                "You are a DnD dungeon master answering questions about your world.",
                " ",
                prompt,
                mode='question'
            )
            pause()

        elif idx == 2:  # Generator
            print("\n" + "-"*70)
            print("Generator Mode creates new lore that integrates with your existing world.")
            print("Examples: 'Create a mysterious tavern', 'Generate a new NPC merchant'\n")
            prompt = input("Generation Prompt: ")
            call_pine_gpt(
                "You are an expert DnD dungeon master creating rich, interconnected campaign world content.",
                " ",
                prompt,
                mode='generator'
            )
            pause()


def pathfinder_tools_menu():
    """Pathfinder Tools submenu."""
    while True:
        display_header("PATHFINDER TOOLS", "Main Menu > Pathfinder Tools")

        options = [
            "Item Generator (weapons, armor, NPCs, monsters, etc.)",
            "Character Location Manager (track character movements)",
            "Shop Profit Calculator (downtime earnings)",
            "Dice Roller"
        ]

        idx, choice = get_choice(options)

        if idx is None:  # Back
            break

        if idx == 0:  # Item Generator
            pathfinder_generator.item_generator_menu()

        elif idx == 1:  # Character Location Manager
            character_manager.character_manager_menu()

        elif idx == 2:  # Shop Calculator
            shop_calculator.shop_calculator_menu()

        elif idx == 3:  # Dice Roller
            pathfinder_generator.dice_roller_interface()


def settings_menu():
    """Settings and configuration menu."""
    while True:
        display_header("SETTINGS", "Main Menu > Settings")

        print("Current Configuration:")
        print(f"  OpenRouter Model: {os.getenv('openrouter_model', 'not set')}")
        print(f"  Embedding Model: {os.getenv('local_embed_model', 'not set')}")
        print(f"  Obsidian Places: {os.getenv('obsidian_places_path', 'not set')}")
        print(f"  Obsidian People: {os.getenv('obsidian_people_path', 'not set')}")
        print(f"  Party Level: {os.getenv('pathfinder_party_level', '3')}")
        print(f"  Party Size: {os.getenv('pathfinder_party_size', '3')}")
        print()

        options = [
            "Update ChromaDB (re-index all lore)",
            "View API key status",
            "View configuration file location"
        ]

        idx, choice = get_choice(options)

        if idx is None:  # Back
            break

        if idx == 0:  # Update ChromaDB
            print("\nUpdating Tags and Creating Lore Dataframe...")
            lore_df = data_code.make_notes_df()
            print("✓ Tags updated")

            if confirm("Update ChromaDB now? (y/n): "):
                chromadb_code.upsert_chromadb(lore_df)
                print("✓ ChromaDB Updated")
            else:
                print("ChromaDB not updated")
            pause()

        elif idx == 1:  # API key status
            api_key = os.getenv('openrouter_api_key')
            if api_key:
                masked = api_key[:10] + "..." if len(api_key) > 10 else "***"
                print(f"\n✓ OpenRouter API key is set: {masked}")
            else:
                print("\n❌ OpenRouter API key is NOT set!")
                print("  Please add 'openrouter_api_key' to your .env file")
            pause()

        elif idx == 2:  # Config file location
            env_path = os.path.join(os.getcwd(), '.env')
            print(f"\nConfiguration file: {env_path}")
            print(f"Exists: {'✓ Yes' if os.path.exists(env_path) else '❌ No'}")
            pause()


def main_menu():
    """Master main menu."""
    while True:
        display_header("WORLDWHISPERER - MASTER CONTROL", None)

        print("Welcome to WorldWhisperer!")
        print("Your integrated D&D/Pathfinder campaign management suite.\n")

        options = [
            "World Lore Manager (ChromaDB-powered Q&A and generation)",
            "Pathfinder Tools (item generation, character tracking, etc.)",
            "Settings (configuration and database management)",
            "Exit"
        ]

        idx, choice = get_choice(options, allow_back=False)

        if idx == 0:  # World Lore
            world_lore_menu()

        elif idx == 1:  # Pathfinder Tools
            pathfinder_tools_menu()

        elif idx == 2:  # Settings
            settings_menu()

        elif idx == 3:  # Exit
            if confirm("Exit WorldWhisperer? (y/n): "):
                print("\nGoodbye! May your campaigns be epic!")
                break


def initialize_system():
    """Initialize the system on startup."""
    load_dotenv()

    print("="*70)
    print(" WORLDWHISPERER - INITIALIZATION")
    print("="*70)

    # Check for tags file
    file_path = 'Notes/tags.csv'
    if not os.path.exists('Notes'):
        print("\n⚠️  Notes directory not found. Creating...")
        os.makedirs('Notes', exist_ok=True)

    if not os.path.exists(file_path):
        print("Creating tags.csv file...")
        with open(file_path, 'w') as file:
            file.write('title, tags\n')

    # Check API key
    if not os.getenv('openrouter_api_key'):
        print("\n⚠️  WARNING: OpenRouter API key not found!")
        print("   Please set 'openrouter_api_key' in your .env file")
        print("   Some features will not work without it.")
        pause()
        return

    # Ask about initial ChromaDB update
    print("\n✓ System initialized")

    if not os.path.exists('chromadb') or not os.listdir('chromadb'):
        print("\n📊 ChromaDB is empty or not initialized.")
        if confirm("Initialize ChromaDB now? (y/n): "):
            print("\nUpdating Tags and Creating Lore Dataframe...")
            lore_df = data_code.make_notes_df()
            print("✓ Complete")

            chromadb_code.upsert_chromadb(lore_df)
            print("✓ ChromaDB Initialized")
    else:
        print("✓ ChromaDB database found")

    print("\nStarting WorldWhisperer...\n")
    pause()


if __name__ == "__main__":
    try:
        initialize_system()
        main_menu()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        print("Please check your configuration and try again.")
        raise