# pip install fastapi uvicorn faiss-cpu sentence-transformers
import json
from pathlib import Path
import numpy as np, faiss
from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, Body

DB = json.loads(Path("base_donnees_chatbot_mastere.json").read_text(encoding="utf-8"))
ITEMS = DB["donnees"]

model = SentenceTransformer("BAAI/bge-m3")  # multilingual, offline-capable
def embed(texts): return np.asarray(model.encode(texts, normalize_embeddings=True), dtype="float32")

corpus_texts = [
    " | ".join([it.get("question",""),
                it.get("reponse",""),
                " ".join(it.get("mots_cles",[])),
                it.get("categorie",""),
                it.get("article_reference","")])
    for it in ITEMS
]
X = embed(corpus_texts)
index = faiss.IndexFlatIP(X.shape[1]); index.add(X)

app = FastAPI()

@app.post("/ask")
def ask(payload: dict = Body(...)):
    q = payload.get("question","")
    qv = embed([q])
    D, I = index.search(qv, 3)
    hits = [ITEMS[i] for i in I[0]]
    top = hits[0]
    return {
        "answer": f"""{top['reponse']}

Citations: [{top.get('article_reference','Règlement UB')}]""",
        "suggestions": [{"id":h["id"], "question":h["question"]} for h in hits[1:]]
    }
