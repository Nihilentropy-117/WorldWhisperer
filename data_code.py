import csv
import os
from pathlib import Path

import pandas as pd

import gpt_code

gpt_override_cost_check = bool(os.getenv('gpt_override_cost_check'))

def make_notes_df():
    notes_dir = Path("Notes")
    tags_file = notes_dir / 'tags.csv'

    # Read tags.csv and create a dictionary with title as key and tags as value
    tags_dict = {}
    if tags_file.exists():
        with tags_file.open('r') as f:
            reader = csv.DictReader(f)
            tags_dict = {row["title"]: row["tags"] for row in reader}

    headers = ['title', 'text', 'tags']
    output_rows = []

    for type_dir in notes_dir.iterdir():
        if type_dir.is_dir():
            for markdown_file in type_dir.glob('*.md'):
                with markdown_file.open('r') as f:
                    text = f.read()

                title = markdown_file.stem
                item_type = type_dir.name

                if title not in tags_dict:
                    print(f"New note found.\nCreating tags for {markdown_file}")
                    file_contents = text
                    tags = gpt_code.gpt4(
                        "You a DnD Dungeon Master AI, master of Vector Databases and Fantasy Lore.",
                        file_contents,
                        """Create a list of up to 10 tags about this Lore entry, for the purpose of 
                        training a vector database. Return only the tags, separated by |"""
                    )

                    tags_dict[title] = tags
                    # Append the new tags to the tags.csv file
                    with tags_file.open('a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([title, tags])
                else:
                    tags = tags_dict[title]

                text = text.strip("\n")
                output_rows.append([title, text, tags])

    notes_df = pd.DataFrame(output_rows, columns=headers)

    return notes_df
