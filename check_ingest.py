"""
Checks completeness of ingested embeddings in Postgres.
Reports missing and zero-row combinations.

Usage:
  python check_ingest.py
"""
import psycopg2
from config import DB_CONFIG, EMBEDDING_DIMS, CHUNK_STRATEGIES, DOCS

MODELS     = list(EMBEDDING_DIMS.keys())
STRATEGIES = list(CHUNK_STRATEGIES.keys())

conn = psycopg2.connect(**DB_CONFIG)
cur  = conn.cursor()

cur.execute("""
    SELECT model_name, document_name, chunk_strategy, COUNT(*) AS rows
    FROM embeddings
    GROUP BY model_name, document_name, chunk_strategy
""")
existing = {(r[0], r[1], r[2]): r[3] for r in cur.fetchall()}
conn.close()

total    = len(MODELS) * len(STRATEGIES) * len(DOCS)
missing  = []
zero_row = []

for model in MODELS:
    for strategy in STRATEGIES:
        for doc in DOCS:
            key = (model, doc, strategy)
            if key not in existing:
                missing.append(key)
            elif existing[key] == 0:
                zero_row.append(key)

done = total - len(missing) - len(zero_row)
print(f"\n{'='*60}")
print(f"Total combinations : {total}")
print(f"OK (rows > 0)      : {done}")
print(f"Missing (no rows)  : {len(missing)}")
print(f"Zero rows          : {len(zero_row)}")
print(f"{'='*60}")

if missing:
    print(f"\n--- MISSING ({len(missing)}) ---")
    for m, d, s in missing:
        print(f"  {m} / {s} / {d}")

if zero_row:
    print(f"\n--- ZERO ROWS ({len(zero_row)}) ---")
    for m, d, s in zero_row:
        print(f"  {m} / {s} / {d}")

if not missing and not zero_row:
    print("\n✓ All combinations ingested successfully!")
