import os
import openai
from pinecone import Pinecone
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Retrieve API keys and host from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_HOST = "https://chain-sense-index-musgrr6.svc.aped-4627-b74a.pinecone.io"

print("PINECONE_API_KEY:", PINECONE_API_KEY)
print("PINECONE_HOST:", PINECONE_HOST)

# Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# Index and embedding model configuration
INDEX_NAME = "chain-sense-index"
EMBEDDING_MODEL = "text-embedding-ada-002"
openai.api_key = OPENAI_API_KEY

# List existing indexes
indexes = pc.list_indexes()
if INDEX_NAME not in [index['name'] for index in indexes]:
    print(f"Index '{INDEX_NAME}' does not exist.")
else:
    print(f"Index '{INDEX_NAME}' exists.")

# Connect to the index
index = pc.Index(host=PINECONE_HOST)

# Path to processed data
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
processed_file_path = os.path.join(BASE_DIR, "data", "processed", "processed_docs.txt")

def chunk_text(text, chunk_size=2000):
    """
    Splits a single large text string into multiple smaller chunks.
    """
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

# Function to get embeddings from OpenAI
def get_embedding(text):
    try:
        response = openai.Embedding.create(
            input=[text],
            engine=EMBEDDING_MODEL
        )
        return response['data'][0]['embedding']
    except Exception as e:
        print(f"Error generating embedding for text: {e}")
        return None

# Load all document lines
with open(processed_file_path, 'r', encoding='utf-8') as f:
    docs = [line.strip() for line in f if line.strip()]

# Chunk the documents if they are too large
chunked_docs = []
for d in docs:
    if len(d) > 2000:
        # If the line is too long, chunk it
        chunked_docs.extend(chunk_text(d, 2000))
    else:
        chunked_docs.append(d)

docs = chunked_docs

# Index the documents in batches
batch_size = 50
num_batches = (len(docs) + batch_size - 1) // batch_size

for i in range(0, len(docs), batch_size):
    batch = docs[i:i+batch_size]
    vectors = []
    for j, doc in enumerate(batch):
        embedding = get_embedding(doc)
        if embedding is None:  # Skip if embedding fails
            continue
        doc_id = f"{i+j}"  # Unique ID for each document
        vectors.append((doc_id, embedding, {"text": doc}))

    # Upsert the batch into Pinecone
    if vectors:
        try:
            index.upsert(vectors=vectors)
            print(f"Upserted batch {i//batch_size + 1}/{num_batches}")
        except Exception as e:
            print(f"Error during upsert: {e}")

print("Indexing complete.")





