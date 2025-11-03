import os
from dotenv import load_dotenv
import data_code
import gpt_code
import chromadb_code


# Define MainMenu
class MainMenu:
    def __init__(self):
        # Menu options and their descriptions
        self.menu_options = {
            "1": "Call ChromaDB GPT (Interactive)",
            "2": "Call ChromaDB GPT (Questions)",
            "3": "Call ChromaDB GPT (Generator)",
            "X": "Exit"
        }

    def __str__(self):
        # Convert menu options to a string for display
        menu_str = "\n".join(f"{key}. {value}" for key, value in self.menu_options.items())
        return f"{menu_str}\n"

    def run(self):
        # Prompt user for input and execute the menu action
        user_choice = input(str(self))
        menu_actions = {
            "1": lambda: call_pine_gpt(
                input("Admin Command: "),
                input("Additional Context: "),
                input("Prompt: "),
                mode='question'
            ),
            "2": lambda: call_pine_gpt(
                "You are a DnD dungeon master answering questions about your world.",
                " ",
                input("Prompt: "),
                mode='question'
            ),
            "3": lambda: call_pine_gpt(
                "You are an expert DnD dungeon master creating rich, interconnected campaign world content.",
                " ",
                input("Generation Prompt: "),
                mode='generator'
            )
        }
        menu_actions.get(user_choice, lambda: None)()


# Call ChromaDB GPT with given parameters
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
        result = gpt_code.gpt4(admin_command, " ", loaded_query)

    print(result)
    return result


# Main execution
if __name__ == "__main__":
    load_dotenv()

    # Check for the existence of a tags file, and create it if it doesn't exist
    file_path = 'Notes/tags.csv'
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            file.write('title, tags\n')

    # Update tags and create a Lore dataframe
    print("Updating Tags and Creating Lore Dataframe")
    lore_df = data_code.make_notes_df()
    print("Complete")

    # Update ChromaDB if the user chooses to do so
    update_chromadb = input("Update ChromaDB Now? y/n")
    if update_chromadb == "y":
        chromadb_code.upsert_chromadb(lore_df)
        print("ChromaDB Updated")
    else:
        print("ChromaDB Not Updated")

    # Run the main menu
    menu = MainMenu()
    menu.run()
