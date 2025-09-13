# Build BM25 + FAISS index from your JSON knowledge base.
# Run:  python index_build.py

import json, re, unicodedata, numpy as np, faiss, pickle
from pathlib import Path
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi

JSON_PATH = Path("./chatbot_database_mastere_ub.json")  # keep in same folder
OUT_DIR = Path("./index")

EMB_MODEL = "BAAI/bge-m3"  # multilingual, works offline once cached

def norm(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"\s+", " ", s).strip()
    return s

def doc_text(it: dict) -> str:
    parts = [
        it.get("question",""),
        it.get("reponse",""),
        " ".join(it.get("mots_cles",[]) or []),
        it.get("categorie",""),
        it.get("article_reference","")
    ]
    return " | ".join(p for p in parts if p)

def main():
    print("Loading JSON from:", JSON_PATH.resolve())
    if not JSON_PATH.exists():
        raise FileNotFoundError(f"Missing {JSON_PATH}")
    db = json.loads(JSON_PATH.read_text(encoding="utf-8"))

    # Accept either {"donnees":[...]} or a raw list
    items = db["donnees"] if isinstance(db, dict) and "donnees" in db else db
    if not isinstance(items, list) or not items:
        raise ValueError("JSON has no 'donnees' list or it's empty.")

    docs = [doc_text(it) for it in items]
    norm_docs = [norm(d) for d in docs]
    print(f"Items: {len(items)}")

    # ---- BM25
    tokenized = [nd.split() for nd in norm_docs]
    bm25 = BM25Okapi(tokenized)

    # ---- Embeddings + FAISS
    print("Loading embedding model:", EMB_MODEL)
    model = SentenceTransformer(EMB_MODEL)
    X = model.encode(norm_docs, normalize_embeddings=True).astype("float32")

    print("Building FAISS index…")
    index = faiss.IndexFlatIP(X.shape[1])
    index.add(X)

    # ---- Save
    OUT_DIR.mkdir(exist_ok=True, parents=True)
    print("Saving index to:", OUT_DIR.resolve())
    np.save(OUT_DIR/"embeddings.npy", X)
    (OUT_DIR/"docs.txt").write_text("\n".join(docs), encoding="utf-8")
    (OUT_DIR/"norm_docs.txt").write_text("\n".join(norm_docs), encoding="utf-8")
    (OUT_DIR/"items.json").write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    with open(OUT_DIR/"bm25.pkl","wb") as f:
        pickle.dump({"bm25": bm25}, f)
    faiss.write_index(index, str(OUT_DIR/"faiss.index"))

    print("Wrote:", [p.name for p in OUT_DIR.iterdir()])
    print("Index built ✔")

if __name__ == "__main__":
    main()
