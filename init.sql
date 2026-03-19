CREATE EXTENSION IF NOT EXISTS vector;

-- Dynamic-dimension approach: store embeddings as float array, cast at query time
CREATE TABLE IF NOT EXISTS embeddings (
  id SERIAL PRIMARY KEY,
  model_name VARCHAR(100) NOT NULL,
  document_name VARCHAR(100) NOT NULL,
  chunk_strategy VARCHAR(50) NOT NULL,
  chunk_id INTEGER NOT NULL,
  chunk_text TEXT NOT NULL,
  embedding_dim INTEGER NOT NULL,
  embedding_data float4[] NOT NULL,
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_embeddings_lookup
  ON embeddings (model_name, document_name, chunk_strategy);

CREATE TABLE IF NOT EXISTS eval_results (
  id SERIAL PRIMARY KEY,
  model_name VARCHAR(100) NOT NULL,
  document_name VARCHAR(100) NOT NULL,
  chunk_strategy VARCHAR(50) NOT NULL,
  question_id VARCHAR(20) NOT NULL,
  question_type VARCHAR(20) NOT NULL,
  retrieved_chunk_ids JSONB,
  retrieved_chunk_texts JSONB,
  recall_at_5 FLOAT,
  mrr FLOAT,
  ndcg_at_5 FLOAT,
  cross_lingual_score FLOAT,
  llm_judge_score FLOAT,
  composite_score FLOAT,
  latency_ms FLOAT,
  created_at TIMESTAMP DEFAULT NOW()
);
