import faiss
import numpy as np
import sqlite3
import json
from openai import OpenAI

import os, getpass

def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")

_set_env("OPENAI_API_KEY")

# Initialize OpenAI
client = OpenAI()

# Create SQLite DB for metadata
conn = sqlite3.connect("metadata.db")
cursor = conn.cursor()

# Create tables for metadata
cursor.executescript("""
CREATE TABLE IF NOT EXISTS classes (
    class_id INTEGER PRIMARY KEY,
    class_name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS frq (
    FRQ_id INTEGER PRIMARY KEY,
    class_id INTEGER,
    FRQ TEXT,
    embed_id INTEGER,
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
);
CREATE TABLE IF NOT EXISTS scoring_guidelines (
    scoring_id INTEGER PRIMARY KEY,
    class_id INTEGER,
    question_id INTEGER,
    scoring_guide_lines TEXT,
    embed_id INTEGER,
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    FOREIGN KEY (question_id) REFERENCES frq(FRQ_id)
);
CREATE TABLE IF NOT EXISTS chief_reader_reports (
    cheif_id INTEGER PRIMARY KEY,
    class_id INTEGER,
    question_id INTEGER,
    cheif_reader_report TEXT,
    embed_id INTEGER,
    FOREIGN KEY (class_id) REFERENCES classes(class_id),
    FOREIGN KEY (question_id) REFERENCES frq(FRQ_id)
);

""")

conn.commit()

# FAISS setup
dimension = 1536  # OpenAI embedding size
index = faiss.IndexFlatL2(dimension)

# Function to generate embeddings
def generate_embedding(text):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return np.array(response.data[0].embedding, dtype="float32")

# Function to add data to FAISS and SQLite
def add_to_faiss(table_name, id_column, text_column, data):
    global index
    for entry in data:
        text = entry[text_column]
        vector = generate_embedding(text)
        vector = np.array(vector, dtype="float32").reshape(1, -1)
        index.add(vector)
        vector_index = index.ntotal  # This is the current number of vectors in the index
        if "question_id" not in entry.keys():
            cursor.execute(f"INSERT INTO {table_name} ({id_column}, class_id, {text_column}, embed_id) VALUES (?, ?, ?, ?)", 
                        (entry[id_column], entry["class_id"], text, vector_index))
        else: 
            cursor.execute(f"INSERT INTO {table_name} ({id_column}, class_id, {text_column}, embed_id, question_id) VALUES (?, ?, ?, ?, ?)", 
                        (entry[id_column], entry["class_id"], text, vector_index, entry['question_id']))
    conn.commit()

# Load input JSON
with open("ex.json", "r") as f:
    data = json.load(f)

# Insert data into SQLite & FAISS
cursor.executemany("INSERT INTO classes (class_id, class_name) VALUES (?, ?)", 
                   [(c["class_id"], c["class_name"]) for c in data["classes"]])

add_to_faiss("frq", "FRQ_id", "FRQ", data=data["frq"])
add_to_faiss("scoring_guidelines", "scoring_id", "scoring_guide_lines",  data = data["scoring_guidelines"])
add_to_faiss("chief_reader_reports", "cheif_id", "cheif_reader_report", data = data["chief_reader_reports"])
#add_to_faiss("sample_responses", "sample_response_id", "sample_response",data = data["sample_responses"]) Eremoved 

# Save FAISS index
faiss.write_index(index, "faiss_index.idx")

print("✅ Data stored successfully in FAISS and SQLite!")

# Function to search for similar FRQs
def search_similar(query_text, top_k=3):
    query_vector = generate_embedding(query_text).reshape(1, -1)
    D, I = index.search(query_vector, top_k)
    results = []
    for idx in I[0]:
        cursor.execute("SELECT FRQ FROM frq WHERE FRQ_id=?", (idx,))
        result = cursor.fetchone()
        if result:
            results.append(result[0])
    return results

# Example search
query = "Find the derivative of a polynomial function."
similar_frqs = search_similar(query)
print(f"🔍 Similar Questions: {similar_frqs}")

conn.close()
