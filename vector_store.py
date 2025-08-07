# import os
# from pinecone import Pinecone, ServerlessSpec
# from dotenv import load_dotenv

# load_dotenv()

# # Load Pinecone API key
# api_key = os.getenv("PINECONE_API_KEY")
# if not api_key:
#     raise ValueError("PINECONE_API_KEY not found in environment variables")

# # Initialize Pinecone
# pc = Pinecone(api_key=api_key)

# # Constants
# INDEX_NAME = "pdf-query-index"
# EMBEDDING_DIMENSION = 384  # Match your embedding model

# # Create the index if it doesn't exist
# if INDEX_NAME not in pc.list_indexes().names():
#     pc.create_index(
#         name=INDEX_NAME,
#         dimension=EMBEDDING_DIMENSION,
#         metric="cosine",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1")
#     )

# # Connect to the index
# index = pc.Index(INDEX_NAME)

# def truncate_text(text, max_bytes=40960):
#     """
#     Truncate the input text so that it doesn't exceed max_bytes in UTF-8.
#     """
#     while len(text.encode("utf-8")) > max_bytes:
#         text = text[:-50]  # remove 50 chars at a time
#     return text

# def upsert_chunks(chunks, embeddings):
#     """
#     Upsert a list of text chunks and their embeddings into Pinecone,
#     truncating metadata to fit size limits.
#     """
#     vectors = []
#     for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
#         safe_text = truncate_text(chunk)
#         vectors.append({
#             "id": f"chunk-{i}",
#             "values": embedding,
#             "metadata": {
#                 "text": safe_text
#             }
#         })
#     index.upsert(vectors=vectors)
#     return index

# def search(query_vector, top_k=5):
#     """
#     Search the index with a vector.
#     """
#     results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
#     return [match['metadata']['text'] for match in results['matches']]
# import os
# from pinecone import Pinecone, ServerlessSpec
# from dotenv import load_dotenv

# load_dotenv()

# # Load API key
# api_key = os.getenv("PINECONE_API_KEY")
# if not api_key:
#     raise ValueError("Missing PINECONE_API_KEY")

# # Init Pinecone
# pc = Pinecone(api_key=api_key)

# # Constants
# INDEX_NAME = "pdf-query-index"
# EMBEDDING_DIM = 384

# # Create index if needed
# if INDEX_NAME not in pc.list_indexes().names():
#     pc.create_index(
#         name=INDEX_NAME,
#         dimension=EMBEDDING_DIM,
#         metric="cosine",
#         spec=ServerlessSpec(cloud="aws", region="us-east-1")
#     )

# # Connect to index
# index = pc.Index(INDEX_NAME)

# def truncate_to_bytes(text, max_bytes=40960):
#     """
#     Truncate text to max byte length in UTF-8 encoding.
#     """
#     encoded = text.encode("utf-8")
#     if len(encoded) <= max_bytes:
#         return text
#     while len(encoded) > max_bytes:
#         text = text[:-10]
#         encoded = text.encode("utf-8")
#     return text

# def upsert_chunks(chunks, embeddings):
#     """
#     Upsert text chunks with embeddings into Pinecone safely.
#     """
#     vectors = []
#     for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
#         safe_text = truncate_to_bytes(chunk)
#         vectors.append({
#             "id": f"chunk-{i}",
#             "values": embedding,
#             "metadata": {"text": safe_text}
#         })
#     # Batch insert
#     index.upsert(vectors=vectors)
#     return index

# def search(query_vector, top_k=5):
#     """
#     Search top-k similar vectors.
#     """
#     results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
#     return [match['metadata']['text'] for match in results['matches']]

import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

# Load API key
api_key = os.getenv("PINECONE_API_KEY")
if not api_key:
    raise ValueError("Missing PINECONE_API_KEY")

# Init Pinecone
pc = Pinecone(api_key=api_key)

# Constants
INDEX_NAME = "pdf-query-index"
EMBEDDING_DIM = 384

# Create index if needed
if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=EMBEDDING_DIM,
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# Connect to index
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
    Split text into chunks of given size with optional overlap.
    """
    chunks = []
    for i in range(0, len(text), chunk_size - overlap):
        chunks.append(text[i:i+chunk_size])
    return chunks

def embed_and_upsert(text, embed_model):
    """
    Split, embed and upsert text into Pinecone.
    """
    chunks = split_text(text, chunk_size=300)
    embeddings = embed_model.encode(chunks)  # assuming sentence-transformers or similar
    return upsert_chunks(chunks, embeddings)

def upsert_chunks(chunks, embeddings):
    """
    Upsert text chunks with embeddings into Pinecone safely.
    """
    vectors = []
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        safe_text = truncate_to_bytes(chunk)
        vectors.append({
            "id": f"chunk-{i}",
            "values": embedding,
            "metadata": {"text": safe_text}
        })
    # Batch insert
    index.upsert(vectors=vectors)
    return index

def search(query_vector, top_k=5):
    """
    Search top-k similar vectors.
    """
    results = index.query(vector=query_vector, top_k=top_k, include_metadata=True)
    return [match['metadata']['text'] for match in results['matches']]
