from re import search
import pandas as pd
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import requests
import sys

# Set pandas display options to show full content
pd.set_option('display.max_colwidth', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
# Load DataFrame (Ensure it's in the same order as when saved)
df = pd.read_csv("journal.csv")
df["Entry"] = df["Entry"].astype(str)  # Ensure text is string type

# Load FAISS index
index = faiss.read_index("journal_index.faiss")
top_k=35
# Load embedder
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")

def get_llm_response(prompt, stream=False, model="llama3:latest"):
    """Helper function to get response from Ollama"""
    response = requests.post('http://localhost:11434/api/generate',
                           json={
                               "model": model,
                               "prompt": prompt,
                               "stream": stream
                           })

    if response.status_code == 200:
        return response.json()['response']
    else:
        return f"Error: {response.status_code}"

def generate_search_terms(question):
    """Generate search terms using the LLM"""
    prompt = f"""Generate 20 specific search terms or phrases in English and French to help find relevant information in a journal about: "{question}"

Format your response as a simple comma-separated list of search terms. Your response should contain only the search terms without any additional text or explanations.
Focus on key events, dates, names, or specific details that might be mentioned in a journal.

For example, if the question is "What did I do on my birthday?", your response should look like:
"birthday, anniversaire, party, cadeau, fête, gifts, cake, gateau, friends..."

Provide only the search terms without any additional text or explanations.
"""

    response = get_llm_response(prompt, model="llama3:latest")
    search_terms = [term.strip() for term in response.split(',')]
    if "search" in search_terms[0]:
        search_terms.pop(0)
    return search_terms

def search_journal(query):
    """Search the journal for the most relevant entries."""
    query_embedding = embedder.encode(query).astype("float32").reshape(1, -1)
    distances, indices = index.search(query_embedding, top_k)

    # Retrieve matching entries
    results = df.iloc[indices[0]].copy()
    results["distance"] = distances[0]  # Add similarity scores
    return results

def search_journal_with_terms(search_terms):
    """Search journal with multiple search terms and combine results"""
    all_results = []
    seen_indices = set()

    for term in search_terms:
        results = search_journal(term)

        # Add new results that weren't seen before
        for _, row in results.iterrows():
            if row.name not in seen_indices:
                all_results.append(row)
                seen_indices.add(row.name)

    # Convert results to DataFrame and sort by distance
    if all_results:
        results_df = pd.DataFrame(all_results).sort_values('distance')
        return results_df.head(top_k)
    return pd.DataFrame()

def generate_answer(question):
    """Main function to generate answers using RAG"""
    # Step 1: Generate search terms
    print("Generating search terms...")
    search_terms = generate_search_terms(question)
    print(f"Search terms: {search_terms}")

    # Step 2: Search journal with generated terms
    print("Searching journal...")
    relevant_entries = search_journal_with_terms(search_terms)
    print(relevant_entries)

    # Format context with dates and times
    context = "\n".join(f"Date: {row['Date']}, Time: {row['Time']}\nEntry: {row['Entry']}"
                       for _, row in relevant_entries.iterrows())

    # Step 3: Generate final answer
    prompt = f"""Based on the following journal entries, please answer this question: {question}

Context from journal:
{context}

Please provide a clear and specific answer based only on the information found in these journal entries. It is your task to analyze the context and provide a relevant answer.
If the information isn't found in the entries, please say so.

Answer:"""

    final_answer = get_llm_response(prompt, model="deepseek-r1:8b")
    return final_answer

# Example usage
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 search_journal.py \"your question here\"")
        sys.exit(1)

    # Get the question from command line arguments
    question = " ".join(sys.argv[1:])

    # Load DataFrame and models only when actually running a search
    df = pd.read_csv("journal.csv")
    df["Entry"] = df["Entry"].astype(str)
    index = faiss.read_index("journal_index.faiss")
    embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")

    answer = generate_answer(question)
    print("\nFinal Answer:")
    print(answer)
