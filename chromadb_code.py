import os
import chromadb
from chromadb.config import Settings
from tqdm.auto import tqdm
from sentence_transformers import SentenceTransformer
from typing import List


def remove_non_ascii(text):
    return ''.join(char for char in text if ord(char) < 128)


# Initialize local embedding model (loaded once, reused across calls)
_embedding_model = None

def get_embedding_model():
    """Lazy-load the embedding model to avoid multiple initializations"""
    global _embedding_model
    if _embedding_model is None:
        model_name = os.getenv('local_embed_model', 'all-MiniLM-L6-v2')
        print(f"Loading local embedding model: {model_name}")
        _embedding_model = SentenceTransformer(model_name)
    return _embedding_model


def create_embeddings(texts: List[str]) -> List[List[float]]:
    """Create embeddings using local sentence-transformers model"""
    model = get_embedding_model()
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    return embeddings.tolist()


def upsert_chromadb(data):
    # Load environment variables for configuration
    collection_name = os.getenv('chromadb_collection_name')
    chromadb_path = os.getenv('chromadb_path', './chromadb')

    print("Upsert to ChromaDB, Batches of 100")
    batch_size = 100

    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=chromadb_path)

    # Get or create collection
    collection = client.get_or_create_collection(
        name=collection_name,
        metadata={"hnsw:space": "cosine"}
    )

    # Process the data in batches
    for i in tqdm(range(0, data.shape[0], batch_size)):
        # Determine the end index of the current batch
        i_end = min(len(data), i + batch_size)
        meta_batch = data[i:i_end]

        # Extract metadata from the batch
        ids_batch = meta_batch['title'].tolist()

        # Prepare the metadata for upserting
        meta_batch_list = [{
            'title': row['title'],
            'text': row['text'],
            'tags': row['tags']
        } for _, row in meta_batch.iterrows()]

        # Prepare documents for embedding (combining title, text, and tags)
        documents = [
            f"NAME: {meta['title']}\nENTRY: {meta['text']}\nTAGS: {meta['tags']}"
            for meta in meta_batch_list
        ]

        # Create embeddings using local model
        embeds = create_embeddings(documents)

        # Convert the IDs to ASCII
        ascii_ids_batch = [remove_non_ascii(id) for id in ids_batch]

        # Upsert the data into ChromaDB
        collection.upsert(
            ids=ascii_ids_batch,
            embeddings=embeds,
            metadatas=meta_batch_list,
            documents=documents
        )


def get_chromadb_context(query, mode='question'):
    """
    Retrieve relevant context from ChromaDB based on query.

    Args:
        query: The user's query/prompt
        mode: 'question' for Q&A or 'generator' for content creation

    Returns:
        Formatted prompt with context and metadata
    """
    # Set environment variables
    collection_name = os.getenv('chromadb_collection_name')
    chromadb_path = os.getenv('chromadb_path', './chromadb')
    top_k = int(os.getenv('top_k', '12'))
    context_limit = int(os.getenv("chromadb_context_limit", "4000"))

    # Embed query using local model
    query_embedding = create_embeddings([query])[0]

    # Initialize ChromaDB client
    client = chromadb.PersistentClient(path=chromadb_path)

    # Get collection
    collection = client.get_collection(name=collection_name)

    # Query ChromaDB
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=['metadatas', 'documents', 'distances']
    )

    # Get contexts from results with relevance scores
    contexts = []
    relevance_data = []

    if results['metadatas'] and len(results['metadatas'][0]) > 0:
        for idx, metadata in enumerate(results['metadatas'][0]):
            distance = results['distances'][0][idx] if results['distances'] else 1.0
            relevance_score = 1 - distance  # Convert distance to similarity

            context_text = f"{metadata['title']}: {metadata['text']}\nTags: {metadata['tags']}"
            contexts.append(context_text)

            relevance_data.append({
                'title': metadata['title'],
                'relevance': relevance_score,
                'tags': metadata['tags']
            })

    # Build prompt based on mode
    if mode == 'generator':
        prompt_start = """Generate new content for this D&D campaign world based on the existing lore below.

IMPORTANT INSTRUCTIONS:
- Ensure consistency with established lore, themes, and tone
- Reference specific existing elements when relevant
- Maintain the world's established rules and constraints
- Create interconnections with existing content
- Match the writing style of existing entries

EXISTING LORE CONTEXT:
"""
        prompt_end = f"\n\nGENERATION REQUEST: {query}\n\nYOUR RESPONSE:"
    else:
        prompt_start = "Answer the question based on the context below.\n\nContext:\n"
        prompt_end = f"\n\nQuestion: {query}\nAnswer:"

    # Build context with character limit
    prompt = ""
    for i in range(1, len(contexts) + 1):
        current_prompt = "\n\n---\n\n".join(contexts[:i])
        if len(current_prompt) >= context_limit:
            prompt = prompt_start + "\n\n---\n\n".join(contexts[:i - 1]) + prompt_end
            break
        elif i == len(contexts):
            prompt = prompt_start + current_prompt + prompt_end

    return prompt, relevance_data