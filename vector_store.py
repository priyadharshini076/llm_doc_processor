import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

# Load Pinecone API key
api_key = os.getenv("PINECONE_API_KEY")
if not api_key:
    raise ValueError("Missing PINECONE_API_KEY")

# Initialize Pinecone
pc = Pinecone(api_key=api_key)

# Constants
INDEX_NAME = "pdf-query-index"
EMBEDDING_DIM = 384  # all-MiniLM-L6-v2 output size

# Create index if it doesn't exist
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Connect to the index
index = pc.Index(INDEX_NAME)

def truncate_to_bytes(text, max_bytes=40960):
    """
    Truncate text to max byte length in UTF-8 encoding.
    """
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text
    while len(encoded) > max_bytes:
        text = text[:-10]
        encoded = text.encode("utf-8")
    return text

def split_text(text, chunk_size=300, overlap=50):
    """
    Split text into overlapping chunks.
    """
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i + chunk_size])
    return chunks

def embed_and_upsert(text, embed_model):
    """
    Split, embed and upsert text chunks into Pinecone.
    """
    chunks = split_text(text)
    embeddings = embed_model.encode(chunks).tolist()
    return upsert_chunks(chunks, embeddings)

def upsert_chunks(chunks, embeddings):
    """
    Upsert vectorized chunks into Pinecone.
    """
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        safe_text = truncate_to_bytes(chunk)
        vectors.append({
            "id": f"chunk-{i}",
            "values": embedding,
            "metadata": {"text": safe_text}
        })

    # Pinecone upsert
    index.upsert(vectors=vectors)
    return index

def search(query_vector, top_k=5):
    """
    Search Pinecone index with query vector.
    """
    results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    return [match['metadata']['text'] for match in results['matches']]
