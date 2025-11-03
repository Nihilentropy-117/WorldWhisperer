import os
import openai
import chromadb
from chromadb.config import Settings
from tqdm.auto import tqdm
from time import sleep


def remove_non_ascii(text):
    return ''.join(char for char in text if ord(char) < 128)


def upsert_chromadb(data):
    # Load environment variables for API keys and configuration
    embed_model = os.getenv('openai_embed_model')
    openai.api_key = os.getenv('openai_api_key')
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
        titles = [f"NAME: {title}" for title in meta_batch['title']]
        texts = [f"ENTRY: {text}" for text in meta_batch['text']]
        tags = [f"TAGS: {tag}" for tag in meta_batch['tags']]

        # Prepare input for embedding creation
        embedding_text = f"{titles}\n{texts}\n{tags}"

        # Create embeddings using OpenAI API with retries for rate limits
        try:
            res = openai.Embedding.create(input=embedding_text, engine=embed_model)
        except:
            done = False
            while not done:
                sleep(5)
                try:
                    res = openai.Embedding.create(input=embedding_text, engine=embed_model)
                    done = True
                except:
                    print("OpenAI Timed Out while creating Embeddings")
                    pass

        # Extract the embeddings from the API response
        embeds = [record['embedding'] for record in res['data']]

        # Prepare the metadata for upserting
        meta_batch_list = [{
            'title': row['title'],
            'text': row['text'],
            'tags': row['tags']
        } for _, row in meta_batch.iterrows()]

        # Convert the IDs to ASCII
        ascii_ids_batch = [remove_non_ascii(id) for id in ids_batch]

        # Prepare documents (combining title, text, and tags)
        documents = [
            f"{meta['title']}: {meta['text']}\n{meta['tags']}"
            for meta in meta_batch_list
        ]

        # Upsert the data into ChromaDB
        collection.upsert(
            ids=ascii_ids_batch,
            embeddings=embeds,
            metadatas=meta_batch_list,
            documents=documents
        )


def get_chromadb_context(query):
    # Set keys and environment variables
    embed_model = os.getenv('openai_embed_model')
    openai.api_key = os.getenv('openai_api_key')
    collection_name = os.getenv('chromadb_collection_name')
    chromadb_path = os.getenv('chromadb_path', './chromadb')
    top_k = int(os.getenv('top_k'))
    context_limit = int(os.getenv("chromadb_context_limit"))

    # Embed query
    res = openai.Embedding.create(input=[query], engine=embed_model)
    query_embedding = res['data'][0]['embedding']

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

    # Get contexts from results
    contexts = []
    if results['metadatas'] and len(results['metadatas'][0]) > 0:
        for metadata in results['metadatas'][0]:
            contexts.append(
                f"{metadata['title']}: {metadata['text']}\n{metadata['tags']}"
            )

    # Build prompt with contexts
    prompt_start = "Respond to the prompt based on the context below.\n\nContext:\n"
    prompt_end = f"\n\nPrompt: {query}\nAnswer:"

    prompt = ""
    for i in range(1, len(contexts) + 1):
        current_prompt = "\n\n---\n\n".join(contexts[:i])
        if len(current_prompt) >= context_limit:
            prompt = prompt_start + "\n\n---\n\n".join(contexts[:i - 1]) + prompt_end
            break
        elif i == len(contexts):
            prompt = prompt_start + current_prompt + prompt_end

    return prompt