"""
Hierarchical menu system for WorldWhisperer.
Provides consistent navigation across all tools.
"""


def clear_screen():
    """Clear the terminal screen (optional, for cleaner UX)."""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def display_header(title, breadcrumb=None):
    """
    Display a formatted header for menus.

    Args:
        title: Main title to display
        breadcrumb: Optional breadcrumb trail (e.g., "Main > Pathfinder Tools")
    """
    print("\n" + "="*70)
    if breadcrumb:
        print(f" {breadcrumb}")
        print("-"*70)
    print(f" {title}")
    print("="*70 + "\n")


def get_choice(options, prompt="Enter your choice: ", allow_back=True):
    """
    Display numbered options and get user choice.

    Args:
        options: List of option strings
        prompt: Prompt to display
        allow_back: If True, add a "Back" option automatically

    Returns:
        Tuple of (choice_index, choice_string) or (None, None) for back
    """
    # Display options
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    if allow_back:
        print(f"  {len(options) + 1}. Back")

    # Get input
    while True:
        try:
            choice = int(input(f"\n{prompt}"))

            if 1 <= choice <= len(options):
                return choice - 1, options[choice - 1]
            elif allow_back and choice == len(options) + 1:
                return None, None
            else:
                print(f"Invalid choice. Please enter a number between 1 and {len(options) + (1 if allow_back else 0)}")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None, None


def confirm(prompt="Are you sure? (y/n): "):
    """
    Get yes/no confirmation from user.

    Args:
        prompt: Confirmation prompt

    Returns:
        Boolean (True for yes, False for no)
    """
    while True:
        response = input(prompt).strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'")


def pause(message="Press Enter to continue..."):
    """Pause and wait for user to press Enter."""
    input(f"\n{message}")