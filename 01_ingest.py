"""
Reads PDFs, chunks text, embeds with specified model, stores in Postgres.

Usage:
  python 01_ingest.py --model text-embedding-3-small --strategy token_512
  python 01_ingest.py --model all --strategy all
  python 01_ingest.py --model all --strategy all --doc shieldauto_th.pdf
  python 01_ingest.py --model all --strategy all --doc shieldauto_th.pdf --doc shieldauto_en.pdf
"""
import argparse, os, time
import pdfplumber
import psycopg2
from psycopg2.extras import execute_values
from config import DB_CONFIG, CHUNK_STRATEGIES, EMBEDDING_DIMS, DOCS_DIR, DOCS
from chunker import get_chunks
from embedder import get_embeddings

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

def ingest(doc_path: str, model_name: str, strategy_name: str, conn):
    config = CHUNK_STRATEGIES[strategy_name]
    doc_name = os.path.basename(doc_path)

    with pdfplumber.open(doc_path) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
    full_text = full_text.replace("\x00", "")  # strip NUL bytes (Postgres rejects them)

    chunks = get_chunks(full_text, strategy_name, config)
    print(f"  {len(chunks)} chunks | {strategy_name} | {doc_name}")

    # Embed in batches of 32
    all_embeddings = []
    for i in range(0, len(chunks), 32):
        batch = chunks[i:i + 32]
        embs = get_embeddings(batch, model_name)
        all_embeddings.extend(embs)
        time.sleep(0.2)

    dim = len(all_embeddings[0]) if all_embeddings else EMBEDDING_DIMS[model_name]

    with conn.cursor() as cur:
        cur.execute(
            "DELETE FROM embeddings WHERE model_name=%s AND document_name=%s AND chunk_strategy=%s",
            (model_name, doc_name, strategy_name)
        )
        execute_values(cur, """
            INSERT INTO embeddings
              (model_name, document_name, chunk_strategy, chunk_id, chunk_text, embedding_dim, embedding_data)
            VALUES %s
        """, [
            (model_name, doc_name, strategy_name, i, chunks[i], dim, list(all_embeddings[i]))
            for i in range(len(chunks))
        ])
    conn.commit()
    print(f"  Stored {len(chunks)} rows -> {model_name}/{strategy_name}/{doc_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="all")
    parser.add_argument("--strategy", default="all")
    parser.add_argument("--doc", action="append", dest="docs", default=None,
                        help="Specific doc filename(s) to ingest (repeatable). Default: all docs in config.")
    args = parser.parse_args()

    models     = list(EMBEDDING_DIMS.keys()) if args.model == "all" else [args.model]
    strategies = list(CHUNK_STRATEGIES.keys()) if args.strategy == "all" else [args.strategy]
    doc_list   = args.docs if args.docs else DOCS
    docs       = [f"{DOCS_DIR}/{d}" for d in doc_list]

    conn = get_conn()
    for model in models:
        for strategy in strategies:
            for doc in docs:
                doc_name = os.path.basename(doc)
                with conn.cursor() as cur:
                    cur.execute(
                        "SELECT COUNT(*) FROM embeddings WHERE model_name=%s AND document_name=%s AND chunk_strategy=%s",
                        (model, doc_name, strategy)
                    )
                    count = cur.fetchone()[0]
                if count > 0:
                    print(f"\nSKIP (exists): {model} / {strategy} / {doc_name} ({count} rows)")
                    continue
                print(f"\nIngesting: {model} / {strategy} / {doc_name}")
                try:
                    ingest(doc, model, strategy, conn)
                except Exception as e:
                    print(f"  ERROR: {e}")
    conn.close()
    print("\nIngestion complete.")
