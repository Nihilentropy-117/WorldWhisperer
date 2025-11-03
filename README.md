# WorldWhisperer - Integrated Campaign Management Suite

**WorldWhisperer** is your all-in-one D&D/Pathfinder campaign management tool, combining AI-powered world lore management with practical tabletop utilities.

## Features Overview

### 🌍 World Lore Manager
- **Local Embeddings**: Free, fast, private vectorization using sentence-transformers
- **OpenRouter Integration**: Access to Claude, GPT-4, Llama, and more
- **Enhanced Generator Mode**: Smart content creation with world consistency checks
- **ChromaDB Storage**: Efficient local vector database
- **Relevance Scoring**: Automatic identification of most relevant lore

### ⚔️ Pathfinder Tools
- **Item Generator**: Create weapons, armor, NPCs, monsters, spells, and more
- **Character Location Manager**: Track character movements across sessions with AI-generated narrative reasons
- **Shop Profit Calculator**: Calculate downtime earnings for player-owned shops
- **Dice Roller**: Quick dice rolling utility

### 🎯 Integrated Features
- **Unified Menu System**: Navigate all tools from one master interface
- **Cross-Tool Integration**: Generated Pathfinder items can be saved to Notes for WorldWhisperer indexing
- **Obsidian Vault Support**: Seamless integration with Obsidian for character/location management
- **Flexible Configuration**: Customize models, paths, and settings via .env file

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
```

Edit `.env` and add your OpenRouter API key:
- Get an API key from https://openrouter.ai/keys
- Add credits (minimum $1)
- Update `openrouter_api_key` in `.env`
- (Optional) Configure Obsidian vault paths for character tracking

### 3. Prepare Your World Notes
1. Create subdirectories in `Notes/` for different content types:
   - `Notes/Characters/`
   - `Notes/Locations/`
   - `Notes/Items/`
   - `Notes/Monsters/`
   - etc.
2. Create `.md` files for each lore item
3. Plain text is supported; markdown formatting will pass through

### 4. Run WorldWhisperer
```bash
python main.py
```

The program will:
- Load the local embedding model (~80MB, one-time download)
- Scan your Notes directory
- Offer to initialize ChromaDB
- Present the master menu

## Master Menu Structure

```
WORLDWHISPERER - MASTER CONTROL
├─ 1. World Lore Manager
│  ├─ Interactive Mode (custom instructions)
│  ├─ Questions Mode (ask about your world)
│  └─ Generator Mode (create new lore)
│
├─ 2. Pathfinder Tools
│  ├─ Item Generator
│  │  ├─ Amulet, Ring, Clothes
│  │  ├─ Magic Weapons & Armor
│  │  ├─ Wands, Staves, Scrolls, Potions
│  │  ├─ Spells
│  │  └─ NPCs & Monsters
│  ├─ Character Location Manager
│  │  ├─ Move characters to random locations
│  │  ├─ Search characters/locations (fuzzy)
│  │  └─ List locations by session
│  ├─ Shop Profit Calculator
│  └─ Dice Roller
│
└─ 3. Settings
   ├─ Update ChromaDB
   ├─ View API key status
   └─ View configuration
```

## Feature Deep Dive

### World Lore Manager

#### Interactive Mode
Full control over the AI interaction:
- Define custom system instructions
- Add specific context
- Perfect for unique queries

#### Questions Mode
Ask questions about your world:
- Queries existing lore via semantic search
- AI answers based on most relevant content
- Great for fact-checking during sessions

#### Generator Mode ✨ **ENHANCED**
Create new content that integrates seamlessly:

**How it works:**
1. Your prompt is analyzed for relevant existing content
2. System identifies most relevant lore items (with relevance scores)
3. AI generates content that:
   - Maintains consistency with established lore
   - References existing elements appropriately
   - Matches your world's tone and style
   - Creates meaningful interconnections

**Example:**
```
Prompt: "Create a mysterious artifact found in the Ancient Ruins"

System finds:
- Ancient Ruins (relevance: 0.92)
- Magic System (relevance: 0.87)
- The Great Collapse (relevance: 0.85)

AI generates artifact that:
- Fits the ruins' established history
- Works within your magic system
- References the Great Collapse event
- Matches existing entry style
```

### Pathfinder Tools

#### Item Generator
Generate complete Pathfinder 1e items with:
- Full game mechanics (stats, bonuses, requirements)
- Detailed descriptions and lore
- Cost and crafting requirements
- Balanced for your party level

**Supported Item Types:**
- Amulets, Rings, Clothes
- Magic Weapons, Magic Armor
- Wands, Staves, Scrolls, Potions
- Spells
- NPCs (with or without stat blocks)
- Monsters

**Save Options:**
- Save to current directory as .md file
- Save to Notes directory for WorldWhisperer indexing (recommended!)

#### Character Location Manager
Track where NPCs are between sessions:

**Features:**
- Randomly assign characters to locations
- AI-generated narrative reasons for movements
- Fuzzy search for characters and places
- View by character or by location
- Session-based tracking (JSONL files)
- Integrates with Obsidian vaults

**Workflow:**
1. Set up character `.md` files in Obsidian (or configure paths)
2. Set up location `.md` files
3. Run "Move characters" for each session
4. AI generates personal reasons for each movement
5. Track movements across campaign

#### Shop Profit Calculator
Calculate Pathfinder 1e downtime earnings:
- Room earnings tracking
- Employee earnings tracking
- Capital expenditure calculation
- Daily/weekly/monthly totals
- Automatic gold piece conversion

### Cross-Tool Integration

**Generated Pathfinder items → World Lore:**
1. Generate an item with Pathfinder Item Generator
2. Choose "Save to Notes directory"
3. Item is automatically categorized (Characters/Monsters/Items)
4. Next ChromaDB update indexes the item
5. Item becomes queryable in World Lore Manager

**Benefits:**
- Seamless workflow
- All content in one searchable database
- Consistent world building
- No duplicate data entry

## Configuration Guide

### Model Selection

Configure different models for different tasks in `.env`:

**World Lore (High Quality):**
```bash
openrouter_model="anthropic/claude-3.5-sonnet"
```

**Pathfinder Generator (Creative):**
```bash
pathfinder_generator_model="anthropic/claude-3.5-sonnet"
```

**Character Manager (Cheap/Free):**
```bash
character_manager_model="google/gemini-2.0-flash-exp:free"
```

### Obsidian Integration

For Character Location Manager:
```bash
obsidian_places_path="/path/to/your/vault/Places"
obsidian_people_path="/path/to/your/vault/People"
```

If you don't use Obsidian, the tool will still work but show warnings.

### Party Defaults

Set default party level and size for item generation:
```bash
pathfinder_party_level="5"
pathfinder_party_size="4"
```

### Embedding Models

Change local embedding quality/speed:
```bash
# Fast, lightweight (default)
local_embed_model="all-MiniLM-L6-v2"

# Better quality, larger
local_embed_model="all-mpnet-base-v2"

# Optimized for Q&A
local_embed_model="multi-qa-mpnet-base-dot-v1"
```

## Cost Optimization

**Typical Usage Costs:**
- **Embeddings**: FREE (local)
- **Tag generation**: ~$0.001 per note
- **World Lore query**: ~$0.01-0.05 per query
- **Item generation**: ~$0.02-0.10 per item
- **Location reasons**: ~$0.00 (free model) to $0.01

**Cost Saving Tips:**
1. Use free model for character location manager
2. Use Haiku for simple queries
3. Use Sonnet only for Generator mode
4. Batch your ChromaDB updates

**Estimated Monthly Cost:**
- Light use (10 queries/week): $1-3
- Medium use (daily sessions): $5-15
- Heavy use (daily + generation): $15-30

## Troubleshooting

### "No module named 'sentence_transformers'"
```bash
pip install sentence-transformers
```

### "OPENROUTER_API_KEY not set"
- Check your `.env` file has the key
- Verify key starts with `sk-or-v1-`
- Ensure `.env` is in the project root directory

### "Embedding dimension mismatch"
- Delete `chromadb/` directory
- Re-run and initialize ChromaDB
- This happens when switching embedding models

### "Characters directory not found"
- Either configure Obsidian paths in `.env`
- Or create character/place `.md` files in the expected locations

### Model download is slow
- First run downloads embedding model (~80MB)
- Subsequent runs are fast
- This is a one-time operation

## Advanced Features

### Batch Operations
Update all lore at once:
1. Main Menu → Settings
2. Update ChromaDB
3. All new/modified notes are indexed

### Session Tracking
Character locations are saved per session:
```
Locations_Session1.jsonl
Locations_Session2.jsonl
...
```

Each entry includes:
- Character name
- Old location
- New location
- AI-generated reason

### Fuzzy Search
Search characters and locations with partial matches:
```
Search: "Tav" → Finds: "Tavern", "Octavia", "Tavish"
```

## Migration from Old Version

If upgrading from standalone WorldWhisperer or PathfinderTools:

1. **Backup your data:**
```bash
cp -r chromadb chromadb_backup
cp -r Notes Notes_backup
```

2. **Update dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure `.env`:**
   - Copy settings from old `.env`
   - Add new Pathfinder settings

4. **Re-initialize ChromaDB:**
   - Delete old `chromadb/` if switching embedding models
   - Run program and choose to initialize

See `MIGRATION_GUIDE.md` for detailed instructions.

## Tips & Best Practices

### World Building
1. Start with core locations and factions
2. Use Generator mode to create interconnected content
3. Save generated items to Notes for indexing
4. Regularly update ChromaDB as your world grows

### Campaign Sessions
1. Use Questions mode during sessions for quick lore lookups
2. Generate items on-the-fly with Pathfinder Tools
3. Track character movements between sessions
4. Use Shop Calculator for downtime activities

### Organization
1. Organize Notes into clear subdirectories
2. Use descriptive filenames
3. Keep consistent formatting
4. Tag items appropriately

### Performance
1. Use faster models for simple tasks
2. Batch ChromaDB updates
3. Keep notes concise but detailed
4. Archive old session data periodically

## Support & Contribution

- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: Check `MIGRATION_GUIDE.md` for more details
- **Configuration**: See `.env.example` for all options

## License

See `LICENSE` file for details.

---

**May your campaigns be epic!** 🎲✨