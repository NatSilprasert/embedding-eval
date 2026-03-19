"""
Runs evaluation for one model x strategy x document combination.

Usage:
  python 02_run_eval.py --model text-embedding-3-small --strategy token_512 --doc technest_th.pdf
"""
import argparse, json, os, time
import numpy as np
import psycopg2
from config import DB_CONFIG, GROUND_TRUTH_DIR, RESULTS_DIR, TOP_K
from metrics import recall_at_k, mean_reciprocal_rank, ndcg_at_k, answer_similarity_score, composite_score
from embedder import get_embeddings


def cosine_sim(a, b):
    a, b = np.array(a, dtype=np.float32), np.array(b, dtype=np.float32)
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom > 0 else 0.0


def retrieve(query_emb, model_name, doc_name, strategy, k, conn):
    """Returns top-k results as (id, chunk_text, similarity, embedding)."""
    with conn.cursor() as cur:
        cur.execute("""
            SELECT id, chunk_text, embedding_data
            FROM embeddings
            WHERE model_name=%s AND document_name=%s AND chunk_strategy=%s
        """, (model_name, doc_name, strategy))
        rows = cur.fetchall()
    if not rows:
        return []
    scored = [(rid, txt, cosine_sim(query_emb, emb), emb) for rid, txt, emb in rows]
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:k]


def find_relevant_ids(keywords, model_name, doc_name, strategy, conn):
    """Find chunk IDs that contain any of the keywords (ground truth proxy)."""
    if not keywords:
        return []
    with conn.cursor() as cur:
        like_clauses = " OR ".join(["chunk_text ILIKE %s"] * len(keywords))
        params = [f"%{kw}%" for kw in keywords] + [model_name, doc_name, strategy]
        cur.execute(f"""
            SELECT id FROM embeddings
            WHERE ({like_clauses})
            AND model_name=%s AND document_name=%s AND chunk_strategy=%s
        """, params)
        return [row[0] for row in cur.fetchall()]


def run_eval_collect(model_name, strategy, doc_name, conn,
                     q_embs=None, a_embs=None):
    """Embed questions+answers, retrieve chunks, compute all metrics per question.

    q_embs / a_embs: optional pre-computed embeddings (list, same order as QA).
    When provided (by 03_run_all.py), no extra embedding API calls are made.
    Returns list of row dicts ready for run_eval_assemble.
    """
    base = doc_name.replace(".pdf", "")
    qa_path = f"{GROUND_TRUTH_DIR}/qa_{base}.json"
    if not os.path.exists(qa_path):
        print(f"  Ground truth not found: {qa_path}")
        return []

    with open(qa_path) as f:
        questions = json.load(f)["questions"]

    # Embed all questions + answers in one batch call if not pre-supplied
    if q_embs is None or a_embs is None:
        texts = [qa["question"] for qa in questions] + [qa["answer"] for qa in questions]
        all_embs = get_embeddings(texts, model_name)
        q_embs = all_embs[:len(questions)]
        a_embs = all_embs[len(questions):]

    rows = []
    for i, qa in enumerate(questions):
        t0 = time.time()

        top_k = retrieve(q_embs[i], model_name, doc_name, strategy, TOP_K, conn)
        latency_ms = (time.time() - t0) * 1000

        retrieved_ids  = [r[0] for r in top_k]
        chunk_embs     = [r[3] for r in top_k]

        relevant_ids = find_relevant_ids(qa.get("relevant_chunk_keywords", []),
                                         model_name, doc_name, strategy, conn)

        rec     = recall_at_k(retrieved_ids, relevant_ids)
        mrr     = mean_reciprocal_rank(retrieved_ids, relevant_ids)
        ndcg    = ndcg_at_k(retrieved_ids, relevant_ids)
        ans_sim = answer_similarity_score(a_embs[i], chunk_embs)
        cross   = rec if qa["type"] == "crosslingual" else None

        rows.append({
            "qa": qa, "rec": rec, "mrr": mrr, "ndcg": ndcg,
            "ans_sim": ans_sim, "cross": cross, "latency_ms": latency_ms,
        })

    return rows


def run_eval_assemble(model_name, strategy, doc_name, rows):
    """Assemble final result dicts from collected rows."""
    results = []
    for row in rows:
        qa   = row["qa"]
        comp = composite_score(row["rec"], row["mrr"], row["ndcg"], row["ans_sim"])
        results.append({
            "model": model_name, "document": doc_name, "strategy": strategy,
            "question_id": qa["id"], "question_type": qa["type"],
            "question": qa["question"],
            "recall_at_5": row["rec"], "mrr": row["mrr"], "ndcg_at_5": row["ndcg"],
            "answer_similarity": row["ans_sim"], "cross_lingual_score": row["cross"],
            "composite_score": comp,
            "retrieval_latency_ms": round(row["latency_ms"], 1),
            "embed_latency_ms": round(row.get("embed_latency_ms", 0), 1),
        })
        print(f"    {qa['id']} [{qa['type']}] composite={comp:.3f} "
              f"ans_sim={row['ans_sim']:.3f} recall={row['rec']:.2f} "
              f"embed={row.get('embed_latency_ms',0):.0f}ms")
    return results


def run_eval(model_name, strategy, doc_name, conn):
    """Single-combination eval. Used by the CLI."""
    rows = run_eval_collect(model_name, strategy, doc_name, conn)
    if not rows:
        return []

    results = run_eval_assemble(model_name, strategy, doc_name, rows)

    os.makedirs(RESULTS_DIR, exist_ok=True)
    out = f"{RESULTS_DIR}/{model_name}_{strategy}_{doc_name.replace('.pdf','')}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {out}")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model",    required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--doc",      required=True)
    args = parser.parse_args()

    conn = psycopg2.connect(**DB_CONFIG)
    run_eval(args.model, args.strategy, args.doc, conn)
    conn.close()
