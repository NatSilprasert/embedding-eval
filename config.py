import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
VOYAGE_API_KEY     = os.environ.get("VOYAGE_API_KEY", "")
COHERE_API_KEY     = os.environ.get("COHERE_API_KEY", "")

DB_CONFIG = {
    "host":     os.environ.get("DB_HOST", "localhost"),
    "port":     int(os.environ.get("DB_PORT", 5433)),
    "database": os.environ.get("DB_NAME", "rag_eval"),
    "user":     os.environ.get("DB_USER", "raguser"),
    "password": os.environ.get("DB_PASSWORD", "ragpass123"),
}

CHUNK_STRATEGIES = {
    "token_512":        {"method": "token",    "size": 512,  "overlap": 0},
    "sentence":         {"method": "sentence", "size": None, "overlap": 0},
    "sliding_512":      {"method": "sliding",  "size": 512,  "overlap": 256},
    "token_500_ov50":   {"method": "token",    "size": 500,  "overlap": 50},
    "token_256_ov32":   {"method": "token",    "size": 256,  "overlap": 32},
}

EMBEDDING_DIMS = {
    # Via OpenRouter (OPENROUTER_API_KEY)
    "bge-m3":                      1024,
    "qwen3-embedding-4b":          2560,
    "qwen3-embedding-8b":          4096,
    "gemini-embedding-001":        3072,
    "text-embedding-3-small":      1536,
    "text-embedding-3-large":      3072,
    # Direct API
    # "voyage-3.5-lite":           1024,   # VOYAGE_API_KEY  (disabled: rate limit)
    "cohere-embed-v3":             1024,   # COHERE_API_KEY
    "cohere-embed-v4":             1536,   # COHERE_API_KEY
    # "gemini-embedding-2-preview":  3072,   # GOOGLE_API_KEY  (disabled)
}

# Cost per 1M tokens in USD — sourced from OpenRouter / provider pricing pages
MODEL_COSTS = {
    "bge-m3":                      0.01,
    "qwen3-embedding-4b":          0.02,
    "qwen3-embedding-8b":          0.05,
    "gemini-embedding-001":        0.15,
    "text-embedding-3-small":      0.02,
    "text-embedding-3-large":      0.13,
    "voyage-3.5-lite":             0.02,
    "cohere-embed-v3":             0.10,
    "cohere-embed-v4":             0.12,
    # "gemini-embedding-2-preview":  0.00,   # free during preview  (disabled)
}

DOCS_DIR         = "./docs"
GROUND_TRUTH_DIR = "./ground_truth"
RESULTS_DIR      = "./results"
TOP_K            = 5
DOCS             = [
    "technest_th.pdf", "technest_en.pdf", "technest_mixed.pdf",
    "stylehub_th.pdf", "stylehub_en.pdf",
    "techmart_th.pdf", "techmart_en.pdf",
    "krungthai_legal_th.pdf", "krungthai_legal_en.pdf",
    "alphacapital_th.pdf", "alphacapital_en.pdf",
    "thailife_th.pdf", "thailife_en.pdf",
    "shieldauto_th.pdf", "shieldauto_en.pdf",
    "neobank_th.pdf", "neobank_en.pdf",
    "datastream_th.pdf", "datastream_en.pdf",
]
