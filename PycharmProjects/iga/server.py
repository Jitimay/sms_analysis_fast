# FastAPI server that answers from the indexed JSON (no hallucinations).
# Run:  uvicorn server:app --host 0.0.0.0 --port 8000

import os, re, json, time, pickle, unicodedata, numpy as np, faiss, requests
from pathlib import Path
from typing import Dict, Any, List
from fastapi import FastAPI, Body
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from rapidfuzz import fuzz

INDEX_DIR = Path("./index")
ITEMS = json.loads((INDEX_DIR/"items.json").read_text(encoding="utf-8"))
NORM_DOCS = (INDEX_DIR/"norm_docs.txt").read_text(encoding="utf-8").splitlines()
EMB = np.load(INDEX_DIR/"embeddings.npy")
FAISS_INDEX = faiss.read_index(str(INDEX_DIR/"faiss.index"))
with open(INDEX_DIR/"bm25.pkl","rb") as f:
    BM25: BM25Okapi = pickle.load(f)["bm25"]

EMB_MODEL = "BAAI/bge-m3"
embedder = SentenceTransformer(EMB_MODEL)

POLISH = os.getenv("POLISH_WITH_OLLAMA","True").lower()=="true"
OLLAMA_URL = os.getenv("OLLAMA_URL","http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL","ub-regs-qa")  # or gpt-oss-20b

def norm(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def rrf(ranks: List[List[int]], k=60):
    scores = {}
    for L in ranks:
        for rank, idx in enumerate(L):
            scores[idx] = scores.get(idx, 0) + 1.0 / (k + rank + 1)
    return [idx for idx,_ in sorted(scores.items(), key=lambda x: x[1], reverse=True)]

def retrieve(query: str, topk=5):
    qn = norm(query)

    # BM25
    bm25_scores = BM25.get_scores(qn.split())
    bm25_top = np.argsort(-bm25_scores)[:20].tolist()

    # Dense
    qv = embedder.encode([qn], normalize_embeddings=True).astype("float32")
    D, I = FAISS_INDEX.search(qv, 20)
    dense_top = I[0].tolist()

    # Fuzzy
    fuzz_scores = [fuzz.WRatio(qn, NORM_DOCS[i]) for i in range(len(NORM_DOCS))]
    fuzz_top = np.argsort(fuzz_scores)[-20:][::-1].tolist()

    fused = rrf([bm25_top, dense_top, fuzz_top])[:topk*2]

    # Final score (simple blend)
    final = []
    for i in fused:
        s = (bm25_scores[i]/(np.max(bm25_scores)+1e-9)) + (fuzz_scores[i]/100.0)
        final.append((s, i))
    final.sort(reverse=True)
    return [idx for _, idx in final[:topk]], (final[0][0] if final else 0.0)

def detect_lang(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ["mbega","ego","ntaco","murakoze","ndabaza","vyose"]): return "KI"
    if any(w in t for w in [" le "," la "," les "," des "," quelle "," quel "," note "," mémoire "," soutenance "]): return "FR"
    return "EN"

def compose_answer(item: Dict[str,Any]) -> str:
    rep = item.get("reponse","").strip()
    art = item.get("article_reference","Règlement UB")
    words = rep.split()
    snippet = " ".join(words[:40]) + ("..." if len(words) > 40 else "")
    return f"""{rep}

Citations: [{art}]
Source snippet: "{snippet}"
"""

def polish(text: str) -> str:
    if not POLISH:
        return text
    try:
        r = requests.post(f"{OLLAMA_URL}/api/generate", json={
            "model": OLLAMA_MODEL,
            "prompt": text,
            "stream": False,
            "options": {"temperature": 0.2, "num_predict": 220}
        }, timeout=120)
        r.raise_for_status()
        return r.json()["response"].strip()
    except Exception:
        return text

class AskPayload(BaseModel):
    question: str

app = FastAPI(title="UB Masters Regulations Bot")

@app.post("/ask")
def ask(payload: AskPayload):
    t0 = time.time()
    idxs, score = retrieve(payload.question, topk=5)
    if not idxs:
        return {"answer":"Désolé, sinshoboye kuronka inyishu. Gerageza gusubiramwo ikibazo.", "latency_ms": int((time.time()-t0)*1000)}

    if score < 0.35:
        return {"answer":"Je ne suis pas sûr de la réponse dans le règlement. Peux-tu préciser la filière / le cas ?", "latency_ms": int((time.time()-t0)*1000)}

    top = ITEMS[idxs[0]]
    answer = compose_answer(top)
    answer = polish(answer)

    suggestions = [{"id": ITEMS[i]["id"], "question": ITEMS[i]["question"]} for i in idxs[1:3]]

    return {
        "answer": answer,
        "citation": top.get("article_reference","Règlement UB"),
        "categorie": top.get("categorie"),
        "importance": top.get("niveau_importance"),
        "related": suggestions,
        "latency_ms": int((time.time()-t0)*1000)
    }

@app.get("/health")
def health():
    return {"status":"ok"}
