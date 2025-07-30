# agents/rag_agent.py

import os
import numpy as np
from pathlib import Path
from sentence_transformers import SentenceTransformer
import faiss
from modules.utils import get_timestamp

# Model (HuggingFace'den)
model = SentenceTransformer("all-MiniLM-L6-v2")  # hızlı & hafif
index = None
texts = []

def build_vector_store(text: str, save_path="vectorstore/index.faiss"):
    global index, texts
    lines = [l.strip() for l in text.split(".") if len(l.strip()) > 10]

    embeddings = model.encode(lines, convert_to_numpy=True)
    dim = embeddings.shape[1]

    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)

    texts = lines

    # Kaydet (opsiyonel)
    os.makedirs(Path(save_path).parent, exist_ok=True)
    faiss.write_index(index, save_path)

    print(f"📚 Vektör deposu oluşturuldu: {len(lines)} cümle")

def search_similar(query: str, top_k=5):
    if index is None:
        raise RuntimeError("❌ Vektör deposu oluşturulmamış.")

    q_embedding = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(q_embedding, top_k)

    return [texts[i] for i in indices[0]]