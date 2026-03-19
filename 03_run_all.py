"""
Runs evaluation for all model x strategy x doc combinations.

Optimization: for each (model, doc) pair, questions and answers are embedded
ONCE and reused across all pending strategies — saving 3× embedding API calls
compared to embedding per combination.

Resume-safe: skips combinations where the result file already exists and is valid JSON.
Logs all outcomes to ./results/run_log.txt.
"""
import importlib, json, os, time
import psycopg2
from config import EMBEDDING_DIMS, RESULTS_DIR, GROUND_TRUTH_DIR, DOCS, DB_CONFIG
from embedder import get_embeddings

_eval = importlib.import_module("02_run_eval")
run_eval_collect  = _eval.run_eval_collect
run_eval_assemble = _eval.run_eval_assemble

STRATEGIES_TO_TEST = ["token_512", "sliding_512", "token_500_ov50", "token_256_ov32"]


def done(model, strategy, doc):
    path = f"{RESULTS_DIR}/{model}_{strategy}_{doc.replace('.pdf','')}.json"
    if not os.path.exists(path):
        return False
    try:
        with open(path) as f:
            json.load(f)
        return True
    except Exception:
        return False  # corrupt/incomplete file → re-run


def load_questions(doc_name):
    base = doc_name.replace(".pdf", "")
    qa_path = f"{GROUND_TRUTH_DIR}/qa_{base}.json"
    if not os.path.exists(qa_path):
        return []
    with open(qa_path) as f:
        return json.load(f)["questions"]


def save(results, model, strategy, doc):
    os.makedirs(RESULTS_DIR, exist_ok=True)
    out = f"{RESULTS_DIR}/{model}_{strategy}_{doc.replace('.pdf','')}.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {out}")


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    conn = psycopg2.connect(**DB_CONFIG)
    log  = open(f"{RESULTS_DIR}/run_log.txt", "a")

    total    = len(EMBEDDING_DIMS) * len(STRATEGIES_TO_TEST) * len(DOCS)
    finished = sum(1 for m in EMBEDDING_DIMS for s in STRATEGIES_TO_TEST for d in DOCS if done(m, s, d))
    print(f"Starting: {finished}/{total} already done\n")

    for model in EMBEDDING_DIMS:
        for doc in DOCS:
            pending = [s for s in STRATEGIES_TO_TEST if not done(model, s, doc)]
            if not pending:
                continue

            questions = load_questions(doc)
            if not questions:
                print(f"  SKIP (no ground truth): {doc}")
                continue

            print(f"\n--- {model} / {doc} | pending: {pending} ---")

            # Pre-embed all questions + answers ONCE for this (model, doc)
            texts    = [qa["question"] for qa in questions] + [qa["answer"] for qa in questions]
            print(f"  Embedding {len(texts)} texts ({len(questions)} Q+A)...")
            t_emb = time.time()
            all_embs = get_embeddings(texts, model)
            embed_elapsed = time.time() - t_emb
            q_embs   = all_embs[:len(questions)]
            a_embs   = all_embs[len(questions):]
            # Per-query embed latency = total batch time / number of questions
            embed_latency_ms = (embed_elapsed / len(questions)) * 1000
            print(f"  Embedded in {embed_elapsed:.1f}s → {embed_latency_ms:.0f}ms/query")

            for strategy in pending:
                print(f"  Evaluating: {strategy}...")
                t0 = time.time()
                try:
                    rows    = run_eval_collect(model, strategy, doc, conn, q_embs, a_embs)
                    for row in rows:
                        row["embed_latency_ms"] = embed_latency_ms
                    results = run_eval_assemble(model, strategy, doc, rows)
                    save(results, model, strategy, doc)
                    elapsed = time.time() - t0
                    log.write(f"OK  | {model:30s} | {strategy:15s} | {doc} | {elapsed:.0f}s\n")
                    log.flush()
                    finished += 1
                    print(f"  Progress: {finished}/{total} ({100*finished/total:.1f}%)")
                except Exception as e:
                    log.write(f"ERR | {model:30s} | {strategy:15s} | {doc} | {e}\n")
                    log.flush()
                    print(f"  ERROR: {e}")

    log.close()
    conn.close()
    print(f"\nAll done. Results in ./{RESULTS_DIR}/")


if __name__ == "__main__":
    main()
