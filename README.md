# RAG Embedding Evaluation Framework

A systematic framework for evaluating embedding models on Thai/English RAG (Retrieval-Augmented Generation) use cases across multiple document domains and chunking strategies.

## Overview

| What | Details |
|------|---------|
| Documents | 19 PDFs across 8 domains — e-commerce, legal, investment, insurance, banking, IT service (Thai + English versions each) |
| Embedding models | 8 models via OpenRouter + Cohere direct API |
| Chunk strategies | 4 strategies (token-512, sliding-512, token-500 ov50, token-256 ov32) |
| Evaluation metrics | Recall@5, MRR, NDCG@5, Answer Similarity, Composite Score |
| Query types | Factual, Multi-hop, Cross-lingual, Summary |
| Total combinations | 8 models × 4 strategies × 19 docs = **608 combinations** |

---

## Project Structure

```
.
├── docs/                          19 synthetic PDFs (Thai + English per domain)
├── ground_truth/                  qa_<doc>.json — 20 Q&As per document
├── results/
│   ├── <model>_<strategy>_<doc>.json   one result file per combination
│   ├── run_log.txt
│   └── plots/
│       ├── eval_results_combined.png        Cost vs composite score (all docs)
│       ├── plot_composite_score.png         Bar charts per strategy
│       ├── plot_answer_similarity.png
│       ├── plot_recall_at_5.png
│       ├── plot_mrr.png
│       ├── plot_ndcg_at_5.png
│       └── plot_strategy_comparison.png     Grouped: model × strategy
├── config.py                      Models, strategies, DB config
├── chunker.py                     Chunking logic (token / sliding window)
├── embedder.py                    Embedding model adapters
├── metrics.py                     All evaluation metrics
├── generate_pdfs.py               Generates all 19 PDFs (TechNest + 16 additional domains)
├── check_ingest.py                Verifies DB completeness
├── 00_generate_ground_truth.py    LLM-generated Q&A per document
├── 01_ingest.py                   Chunk → embed → store in PostgreSQL
├── 02_run_eval.py                 Evaluate one model × strategy × doc
├── 03_run_all.py                  Resume-safe full sweep
├── 04_plot_results.py             Scatter: cost vs composite score
├── 05_plot_metrics.py             Bar charts per metric
├── 06_plot_selected_models.py     Scatter for selected models (CLI: pass model keys as args)
├── 07_plot_strategy_comparison.py Grouped bars: model × strategy
├── docker-compose.yml             PostgreSQL + pgvector
├── init.sql                       DB schema
├── ANALYSIS.md                    Detailed analysis of evaluation results
├── .env                           API keys (git-ignored)
└── .env.example                   Template
```

---

## Evaluation Metrics

### Recall@5
**"Did we retrieve at least one relevant chunk in the top 5?"**

Measures the fraction of relevant chunks found in the top-K retrieved results.

```
Recall@K = |retrieved[:K] ∩ relevant| / |relevant|
```

- Relevant chunks are identified by keyword matching (`relevant_chunk_keywords` in ground truth)
- If no keywords match any chunk, Recall = 0 (honest — not inflated)
- Range: 0–1, higher is better

---

### MRR — Mean Reciprocal Rank
**"How high does the first relevant chunk appear?"**

Rewards models that rank the relevant chunk near the top.

```
MRR = 1 / rank_of_first_relevant_chunk
```

- First result relevant → MRR = 1.0
- Relevant chunk at rank 3 → MRR = 0.33
- No relevant chunk in top K → MRR = 0
- Range: 0–1, higher is better

---

### NDCG@5 — Normalized Discounted Cumulative Gain
**"How well is the ranking ordered?"**

Measures ranking quality by giving higher credit to relevant chunks appearing earlier.

```
DCG@K  = Σ relevance_i / log2(i + 2)
NDCG@K = DCG@K / ideal_DCG@K
```

- Accounts for position: a relevant result at rank 1 scores better than at rank 5
- Normalized 0–1 against the best possible ranking (ideal DCG)
- Range: 0–1, higher is better

---

### Answer Similarity
**"Are the retrieved chunks semantically close to the correct answer?"**

Embeds the expected answer using the **same model being evaluated**, then measures the average cosine similarity between the answer embedding and the top-3 retrieved chunk embeddings.

```
answer_sim = avg(cosine_sim(answer_emb, chunk_emb) for chunk_emb in top_3_chunks)
```

- Uses the model's own embedding space → directly measures the model's semantic alignment
- Does not require any external LLM call → deterministic and free
- Especially meaningful for multilingual evaluation (cross-lingual proximity)
- Range: 0–1, higher is better

---

### Composite Score
**"Overall weighted performance."**

A single weighted score combining all four metrics:

```
composite = answer_sim × 0.30
          + recall     × 0.30
          + ndcg       × 0.25
          + mrr        × 0.15
```

| Metric | Weight | Rationale |
|--------|--------|-----------|
| Answer Similarity | 30% | Semantic quality of retrieved content |
| Recall@5 | 30% | Whether relevant content is retrieved at all |
| NDCG@5 | 25% | Quality of the ranking order |
| MRR | 15% | Position of the first hit |

> `cross_lingual_score` is tracked separately in result JSON (= Recall for crosslingual questions) but excluded from the composite to avoid double-counting Recall.

---

## Embedding Models

| Model key | Provider | Dimensions | Cost / 1M tokens |
|-----------|----------|-----------|-----------------|
| `bge-m3` | OpenRouter (BAAI) | 1024 | $0.01 |
| `qwen3-embedding-4b` | OpenRouter (Qwen) | 2560 | $0.02 |
| `qwen3-embedding-8b` | OpenRouter (Qwen) | 4096 | $0.05 |
| `gemini-embedding-001` | OpenRouter (Google) | 3072 | $0.15 |
| `text-embedding-3-small` | OpenRouter (OpenAI) | 1536 | $0.02 |
| `text-embedding-3-large` | OpenRouter (OpenAI) | 3072 | $0.13 |
| `cohere-embed-v3` | Cohere (direct) | 1024 | $0.10 |
| `cohere-embed-v4` | Cohere (direct) | 1536 | $0.12 |

---

## Chunking Strategies

| Strategy | Method | Size (tokens) | Overlap |
|----------|--------|---------------|---------|
| `token_512` | Hard token split | 512 | 0 |
| `sliding_512` | Sliding window | 512 | 256 |
| `token_500_ov50` | Token + overlap | 500 | 50 |
| `token_256_ov32` | Token + overlap | 256 | 32 |

Chunking is done using `tiktoken` (`cl100k_base`) for consistent token counting across all models.

---

## Setup

### 1. Install dependencies

```bash
pip install reportlab pdfplumber psycopg2-binary tiktoken numpy matplotlib \
            requests python-dotenv
```

### 2. Configure API keys

```bash
cp .env.example .env
# Fill in your keys
```

| Key | Required for |
|-----|-------------|
| `OPENROUTER_API_KEY` | All OpenRouter embedding models + ground truth generation |
| `COHERE_API_KEY` | `cohere-embed-v3`, `cohere-embed-v4` |

### 3. Start PostgreSQL + pgvector

```bash
docker-compose up -d
until docker-compose exec postgres pg_isready -U raguser -d rag_eval; do sleep 2; done
```

### 4. Generate PDFs

```bash
python generate_pdfs.py
```

---

## Running the Evaluation

```bash
# Step 1 — Generate ground truth Q&A (skips already-generated files)
python 00_generate_ground_truth.py

# Step 2 — Ingest all models × all strategies
python 01_ingest.py

# Step 3 — Verify ingestion is complete
python check_ingest.py

# Step 4 — Run full evaluation (resume-safe, ~30 min)
python 03_run_all.py

# Step 5 — Generate all plots
python 04_plot_results.py
python 05_plot_metrics.py
python 06_plot_selected_models.py
python 07_plot_strategy_comparison.py
```

### Single combination (for debugging)

```bash
python 02_run_eval.py --model bge-m3 --strategy token_512 --doc technest_th.pdf
```

---

## Output Plots

| File | Script | Description |
|------|--------|-------------|
| `eval_results_combined.png` | `04_plot_results.py` | Scatter: cost vs composite score — Thai / English / Combined |
| `plot_composite_score.png` | `05_plot_metrics.py` | Horizontal bar: composite score per model × strategy |
| `plot_answer_similarity.png` | `05_plot_metrics.py` | Horizontal bar: answer similarity per model × strategy |
| `plot_recall_at_5.png` | `05_plot_metrics.py` | Horizontal bar: recall per model × strategy |
| `plot_mrr.png` | `05_plot_metrics.py` | Horizontal bar: MRR per model × strategy |
| `plot_ndcg_at_5.png` | `05_plot_metrics.py` | Horizontal bar: NDCG per model × strategy |
| `eval_results_selected_models.png` | `06_plot_selected_models.py` | Scatter: cost vs composite for user-selected models |
| `plot_strategy_comparison.png` | `07_plot_strategy_comparison.py` | Grouped bar: compare 4 strategies side-by-side per model |

### Selecting models for `06_plot_selected_models.py`

```bash
# Default: qwen3-8b, qwen3-4b, gemini-embedding-001
python 06_plot_selected_models.py

# Custom selection
python 06_plot_selected_models.py bge-m3 gemini-embedding-001 cohere-embed-v3

# All 8 models
python 06_plot_selected_models.py bge-m3 qwen3-embedding-4b qwen3-embedding-8b \
    gemini-embedding-001 text-embedding-3-small text-embedding-3-large \
    cohere-embed-v3 cohere-embed-v4
```

---

## Notes

- **Resume safety**: `03_run_all.py` validates existing result files (JSON parse check) and skips complete ones — safe to interrupt and restart.
- **No LLM judge**: Evaluation is fully deterministic using embedding-based Answer Similarity. No external LLM calls during eval → fast (~30 min) and free.
- **Embeddings stored as `float4[]`** in PostgreSQL/pgvector to accommodate variable dimensions across models. Cosine similarity is computed in Python (NumPy).
- **Cross-lingual score** is tracked per question in the result JSON for analysis but not included in the composite to avoid double-counting Recall.
