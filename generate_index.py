import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os

os.environ["OMP_NUM_THREADS"] = "2"
os.environ["MKL_NUM_THREADS"] = "2"
print("Reading CSV")
df = pd.read_csv("journal.csv")
df["Entry"] = df["Entry"].astype(str)  # Ensure text is string type

print("Initializing embedder")
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")

# Process embeddings in batches to avoid memory overflow
batch_size = 64
embeddings = []

print("Entering loop")
for i in range(0, len(df), batch_size):
    batch = df["Entry"].iloc[i : i + batch_size].tolist()
    batch_embeddings = embedder.encode(batch)
    embeddings.extend(batch_embeddings)
    print("loop " + str(i) + " of " + str(len(df)))

# Convert list of embeddings to NumPy array
print("convert list of embeddings to NumPy array")
embeddings = np.array(embeddings, dtype="float32")

# Initialize FAISS index
print("Initializing FAISS index...")
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

# Save index
faiss.write_index(index, "journal_index.faiss")
