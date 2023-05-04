import os
from dotenv import load_dotenv
import data_code
import gpt_code
import pinecone_code


# Define MainMenu
class MainMenu:
    def __init__(self):
        # Menu options and their descriptions
        self.menu_options = {
            "1": "Call PineconeGPT (Interactive)",
            "2": "Call PineconeGPT (Questions)",
            "3": "Call PineconeGPT (Generator)",
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
                input("Prompt: ")
            ),
            "2": lambda: call_pine_gpt(
                "You are a DnD dungeon master answering questions about your world.",
                " ",
                input("Prompt: ")
            ),
            "3": lambda: call_pine_gpt(
                "You are a DnD dungeon master writing a campaign world.",
                " ",
                input("Prompt: ")
            )
        }
        menu_actions.get(user_choice, lambda: None)()


# Call PineconeGPT with given parameters
def call_pine_gpt(admin_command=None, additional_context=None, prompt=None):
    loaded_query = pinecone_code.get_pinecone_context(prompt + "\n" + additional_context)
    # print(loaded_query)
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

    # Update Pinecone if the user chooses to do so
    update_pinecone = input("Update Pinecone Now? y/n")
    if update_pinecone == "y":
        pinecone_code.upsert_pinecone(lore_df)
        print("Pinecone Updated")
    else:
        print("Pinecone Not Updated")

    # Run the main menu
    menu = MainMenu()
    menu.run()
