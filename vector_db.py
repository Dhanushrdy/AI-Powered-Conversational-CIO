import chromadb
from chromadb.config import Settings
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "chroma_data")

# Initialize ChromaDB client persistent storage
client = chromadb.PersistentClient(path=DB_PATH)

def get_chroma_client():
    return client

def get_collection(name: str):
    # Returns an existing collection or creates a new one
    return client.get_or_create_collection(name=name)
