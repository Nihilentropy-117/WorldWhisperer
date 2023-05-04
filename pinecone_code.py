import os
import openai
import pinecone
from tqdm.auto import tqdm
from time import sleep


class PineconeContext:
    def __init__(self, api_key, environment):
        self.api_key = api_key
        self.environment = environment

    def __enter__(self):
        pinecone.init(api_key=self.api_key, environment=self.environment)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


def remove_non_ascii(text):
    return ''.join(char for char in text if ord(char) < 128)


def upsert_pinecone(data):
    # Load environment variables for API keys and configuration
    embed_model = os.getenv('openai_embed_model')
    openai.api_key = os.getenv('openai_api_key')
    pinecone_api_key = os.getenv('pinecone_api_key')
    pinecone_environment = os.getenv("pinecone_environment")
    pinecone_index_name = os.getenv('pinecone_index_name')

    print("Upsert to Pinecone, Batches of 100")
    batch_size = 100

    # Initialize Pinecone outside the loop
    with PineconeContext(api_key=pinecone_api_key, environment=pinecone_environment):
        # Get or create the Pinecone index
        index = pinecone.Index(pinecone_index_name)
        if pinecone_index_name not in pinecone.list_indexes():
            index_dimension = None
        else:
            describe_index = pinecone.describe_index(pinecone_index_name)

            index_dimension = describe_index[3]
            b = 2
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

            # Create the index if it does not exist
            if index_dimension is None:
                index_dimension = len(embeds[0])
                pinecone.create_index(pinecone_index_name, dimension=index_dimension, metric='cosine')

            # Prepare the metadata for upserting
            meta_batch_list = [{
                'title': row['title'],
                'text': row['text'],
                'tags': row['tags']
            } for _, row in meta_batch.iterrows()]

            # Convert the IDs to ASCII
            ascii_ids_batch = [remove_non_ascii(id) for id in ids_batch]

            # Prepare the data for upserting into Pinecone
            to_upsert = list(zip(ascii_ids_batch, embeds, meta_batch_list))

            # Upsert the data into Pinecone
            index.upsert(vectors=to_upsert)


def get_pinecone_context(query):
    # Set keys and environment variables
    embed_model = os.getenv('openai_embed_model')
    openai.api_key = os.getenv('openai_api_key')
    pinecone_api_key = os.getenv('pinecone_api_key')
    pinecone_environment = os.getenv("pinecone_environment")
    pinecone_index_name = os.getenv('pinecone_index_name')
    pinecone_top_k = int(os.getenv('top_k'))
    pinecone_context_limit = int(os.getenv("pinecone_context_limit"))

    # Embed query
    res = openai.Embedding.create(input=[query], engine=embed_model)
    xq = res['data'][0]['embedding']

    # Initialize Pinecone
    pinecone.init(api_key=pinecone_api_key, environment=pinecone_environment)
    index = pinecone.Index(pinecone_index_name)

    # Query Pinecone
    res = index.query(xq, top_k=pinecone_top_k, include_metadata=True)

    # Get contexts
    contexts = [
        f"{x['metadata']['title']}: {x['metadata']['text']}\n{x['metadata']['tags']}" for x in res['matches']
    ]

    # Build prompt with contexts
    prompt_start = "Respond to the prompt based on the context below.\n\nContext:\n"
    prompt_end = f"\n\nPrompt: {query}\nAnswer:"

    prompt = ""
    for i in range(1, len(contexts) + 1):
        current_prompt = "\n\n---\n\n".join(contexts[:i])
        if len(current_prompt) >= pinecone_context_limit:
            prompt = prompt_start + "\n\n---\n\n".join(contexts[:i - 1]) + prompt_end
            break
        elif i == len(contexts):
            prompt = prompt_start + current_prompt + prompt_end

    return prompt
