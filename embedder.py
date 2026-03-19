import os, requests
from typing import List
from dotenv import load_dotenv

load_dotenv()

# ─── OpenRouter model IDs ─────────────────────────────────────────────────────
OPENROUTER_MODEL_IDS = {
    "bge-m3":                 "baai/bge-m3",
    "qwen3-embedding-4b":     "qwen/qwen3-embedding-4b",
    "qwen3-embedding-8b":     "qwen/qwen3-embedding-8b",
    "gemini-embedding-001":   "google/gemini-embedding-001",
    "text-embedding-3-small": "openai/text-embedding-3-small",
    "text-embedding-3-large": "openai/text-embedding-3-large",
}


def embed_openrouter(texts: List[str], model_name: str) -> List[List[float]]:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    if not key:
        raise ValueError("OPENROUTER_API_KEY is not set in .env")
    resp = requests.post(
        "https://openrouter.ai/api/v1/embeddings",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": OPENROUTER_MODEL_IDS[model_name], "input": texts},
        timeout=60,
    )
    resp.raise_for_status()
    data = sorted(resp.json()["data"], key=lambda x: x["index"])
    return [item["embedding"] for item in data]


def embed_voyage(texts: List[str]) -> List[List[float]]:
    """Direct Voyage AI API — needs VOYAGE_API_KEY (dash.voyageai.com/api-keys)"""
    key = os.environ.get("VOYAGE_API_KEY", "")
    if not key:
        raise ValueError("VOYAGE_API_KEY is not set in .env")
    # Simple retry with backoff to handle 429 rate limits gracefully
    last_error = None
    for attempt in range(3):
        resp = requests.post(
            "https://api.voyageai.com/v1/embeddings",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": "voyage-3.5-lite", "input": texts, "input_type": "document"},
            timeout=60,
        )
        if resp.status_code == 429:
            # Too Many Requests – backoff and retry
            retry_after = resp.headers.get("Retry-After")
            try:
                sleep_sec = int(retry_after)
            except (TypeError, ValueError):
                sleep_sec = 5 * (attempt + 1)
            print(f"Voyage 429: backing off for {sleep_sec}s (attempt {attempt+1}/3)")
            import time
            time.sleep(sleep_sec)
            last_error = requests.exceptions.HTTPError(f"429 Too Many Requests: {resp.text[:200]}")
            continue
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            last_error = e
            break
        body = resp.json()
        if "data" not in body:
            raise RuntimeError(f"Unexpected Voyage embedding response: {str(body)[:200]}")
        data = sorted(body["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in data]
    # If we exit the loop without returning, propagate the last error
    if last_error:
        raise last_error
    raise RuntimeError("Voyage embedding request failed without a specific error")


def embed_cohere(texts: List[str], model_name: str) -> List[List[float]]:
    """Direct Cohere API — needs COHERE_API_KEY (dashboard.cohere.com/api-keys)"""
    import time
    key = os.environ.get("COHERE_API_KEY", "")
    if not key:
        raise ValueError("COHERE_API_KEY is not set in .env")
    cohere_model = {
        "cohere-embed-v3": "embed-multilingual-v3.0",
        "cohere-embed-v4": "embed-v4.0",
    }[model_name]
    last_error = None
    for attempt in range(5):
        resp = requests.post(
            "https://api.cohere.com/v2/embed",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            json={"model": cohere_model, "texts": texts, "input_type": "search_document",
                  "embedding_types": ["float"]},
            timeout=60,
        )
        if resp.status_code == 429:
            retry_after = resp.headers.get("Retry-After")
            try:
                sleep_sec = int(retry_after)
            except (TypeError, ValueError):
                sleep_sec = 10 * (attempt + 1)
            print(f"Cohere 429: backing off {sleep_sec}s (attempt {attempt+1}/5)")
            time.sleep(sleep_sec)
            last_error = requests.exceptions.HTTPError(f"429 Too Many Requests: {resp.text[:200]}")
            continue
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as e:
            last_error = e
            break
        return resp.json()["embeddings"]["float"]
    if last_error:
        raise last_error
    raise RuntimeError("Cohere embedding request failed without a specific error")


def embed_google(texts: List[str], model_name: str) -> List[List[float]]:
    """Direct Google AI API — needs GOOGLE_API_KEY (aistudio.google.com/apikey)"""
    import time
    key = os.environ.get("GOOGLE_API_KEY", "")
    if not key:
        raise ValueError("GOOGLE_API_KEY is not set in .env")
    google_model = "gemini-embedding-2-preview"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{google_model}:batchEmbedContents"

    def _batch(batch_texts: List[str]) -> List[List[float]]:
        payload = [
            {
                "model": f"models/{google_model}",
                "content": {"parts": [{"text": t}]},
                "taskType": "RETRIEVAL_DOCUMENT",
            }
            for t in batch_texts
        ]
        for attempt in range(5):
            resp = requests.post(
                url,
                params={"key": key},
                headers={"Content-Type": "application/json"},
                json={"requests": payload},
                timeout=60,
            )
            if resp.status_code == 429:
                sleep_sec = 10 * (attempt + 1)
                print(f"Google 429: backing off {sleep_sec}s (attempt {attempt+1}/5)")
                time.sleep(sleep_sec)
                continue
            resp.raise_for_status()
            return [item["values"] for item in resp.json()["embeddings"]]
        resp.raise_for_status()

    # Google batchEmbedContents limit is 100 per call
    batch_size = 100
    results: List[List[float]] = []
    for i in range(0, len(texts), batch_size):
        results.extend(_batch(texts[i : i + batch_size]))
        if i + batch_size < len(texts):
            time.sleep(1)  # small pause between batches
    return results


def get_embeddings(texts: List[str], model_name: str) -> List[List[float]]:
    if model_name in OPENROUTER_MODEL_IDS:
        return embed_openrouter(texts, model_name)
    if model_name == "voyage-3.5-lite":
        return embed_voyage(texts)
    if model_name in ("cohere-embed-v3", "cohere-embed-v4"):
        return embed_cohere(texts, model_name)
    if model_name == "gemini-embedding-2-preview":
        return embed_google(texts, model_name)
    raise ValueError(
        f"Unknown model: {model_name!r}. "
        f"Available: {list(OPENROUTER_MODEL_IDS) + ['voyage-3.5-lite', 'cohere-embed-v3', 'cohere-embed-v4', 'gemini-embedding-2-preview']}"
    )
