import os
import faiss
import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from rank_bm25 import BM25Okapi
from dotenv import load_dotenv
from openai import OpenAI

# ------------------- Load Environment -------------------
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=api_key)

# ------------------- FastAPI App -------------------
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ------------------- Load FAISS + Metadata -------------------
FAISS_INDEX_FILE = "constitution.index"
EMBEDDINGS_FILE = "embeddings.npy"
METADATA_CSV_FILE = "constitution_metadata.csv"

index = faiss.read_index(FAISS_INDEX_FILE)
embeddings = np.load(EMBEDDINGS_FILE)
metadata = pd.read_csv(METADATA_CSV_FILE)
metadata_dicts = metadata.to_dict(orient="records")

# ------------------- BM25 -------------------
texts = [row["text"] for row in metadata_dicts]
bm25 = BM25Okapi([t.split() for t in texts])

# ------------------- Query Decomposition -------------------
def decompose_query(query):
    return [q.strip() for q in query.replace(";", ",").split(",") if q.strip()]

# ------------------- Retrieval with RAG Fusion -------------------
def retrieve_candidates(query, top_k=5):
    candidate_indices = set()
    for subq in decompose_query(query):
        # BM25
        bm25_scores = bm25.get_scores(subq.split())
        bm25_top = np.argsort(bm25_scores)[::-1][:top_k]
        # Dense embedding
        q_emb = client.embeddings.create(
            model="text-embedding-3-large",
            input=subq
        ).data[0].embedding
        q_emb = np.array(q_emb, dtype="float32").reshape(1, -1)
        _, I = index.search(q_emb, top_k)
        for idx in set(bm25_top).union(I[0]):
            candidate_indices.add(idx)
    return [metadata_dicts[i] for i in candidate_indices]

# ------------------- Legal Prompt Template -------------------
def build_legal_prompt(query, retrieved_chunks):
    context = "\n\n".join([
        f"Section {c['section_number']} ({c['section_title']}): {c['text']}"
        for c in retrieved_chunks
    ])
    prompt = f"""
You are a legal reasoning assistant. Use only the provided constitutional text.
Answer the query strictly using legal terminology and citations.

Query: {query}

Relevant sections from the Constitution:
{context}

Answer in a professional legal manner, citing relevant sections wherever applicable:
"""
    return prompt

# ------------------- Generate Answer -------------------
def generate_answer(query):
    candidates = retrieve_candidates(query, top_k=5)
    if not candidates:
        return "No relevant sections found in the Constitution."
    prompt = build_legal_prompt(query, candidates)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content

# ------------------- Routes -------------------
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask", response_class=JSONResponse)
def ask(query: str = Form(...)):
    answer = generate_answer(query)
    return {"query": query, "answer": answer}

# ------------------- Run locally -------------------
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
