"""
Reads each PDF using pdfplumber, sends text to OpenRouter, saves structured Q&A pairs.

Usage:
  python 00_generate_ground_truth.py
"""
import os, json
from datetime import datetime
import pdfplumber
import requests
from config import OPENROUTER_API_KEY, JUDGE_MODEL, DOCS_DIR, GROUND_TRUTH_DIR, DOCS


def call_openrouter(system_prompt: str, user_prompt: str) -> str:
    """
    Thin wrapper around OpenRouter chat completions.
    Raises a clear error when the response doesn't contain choices (e.g. auth / quota issues).
    """
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": JUDGE_MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": 0.3,
        },
    )

    try:
        data = response.json()
    except Exception as e:
        raise RuntimeError(f"OpenRouter returned non‑JSON response: {e}, text={response.text[:500]!r}")

    if response.status_code != 200:
        raise RuntimeError(
            f"OpenRouter error {response.status_code}: {data.get('error') or data}"
        )

    choices = data.get("choices")
    if not choices:
        raise RuntimeError(f"OpenRouter response missing 'choices': {data}")

    return choices[0]["message"]["content"]

SYSTEM_PROMPT = """You are a QA dataset generator for a RAG evaluation system.
Given document text, generate exactly 20 question-answer pairs in JSON format.
Generate 5 questions per type:
- "factual": single-hop, requires one exact value from text (number, date, SKU code, price, name)
- "multihop": requires combining information from 2 or more different sections of the document
- "crosslingual": write the question as a mix of Thai and English in one sentence (code-switching style), answer in same language as the source document
- "summary": requires summarizing or comparing multiple items or sections

Rules:
- Every question must be answerable ONLY from the provided document text, not from general knowledge
- Answers must be specific and include the approximate page or section where the answer is found
- For factual questions, include the exact value (number, code, date) in the answer
- Return ONLY valid JSON with no other text, no markdown backticks

Output format:
{
  "questions": [
    {
      "id": "q001",
      "type": "factual",
      "question": "...",
      "answer": "...",
      "source_section": "approximate section name or page number",
      "relevant_chunk_keywords": ["keyword1", "keyword2", "keyword3"]
    }
  ]
}"""

def generate_qa_for_doc(doc_path: str) -> dict:
    doc_name = os.path.basename(doc_path)
    base = doc_name.replace(".pdf", "")
    print(f"\nGenerating Q&A for: {doc_name}")

    with pdfplumber.open(doc_path) as pdf:
        full_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    # Truncate to avoid token limits (keep first ~15000 chars)
    user_prompt = f"Document: {doc_name}\n\n{full_text[:15000]}"

    raw = call_openrouter(SYSTEM_PROMPT, user_prompt)

    # Parse JSON
    try:
        data = json.loads(raw.strip())
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code block if present
        import re
        match = re.search(r'```(?:json)?\s*(\{.*\})\s*```', raw, re.DOTALL)
        if match:
            data = json.loads(match.group(1))
        else:
            print(f"  WARNING: Could not parse JSON for {doc_name}. Raw:\n{raw[:500]}")
            data = {"questions": []}

    result = {
        "document": doc_name,
        "generated_at": datetime.utcnow().isoformat(),
        "total_questions": len(data.get("questions", [])),
        "questions": data.get("questions", [])
    }

    os.makedirs(GROUND_TRUTH_DIR, exist_ok=True)
    out_path = f"{GROUND_TRUTH_DIR}/qa_{base}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"  Saved {result['total_questions']} Q&As -> {out_path}")
    return result

if __name__ == "__main__":
    if not OPENROUTER_API_KEY:
        raise ValueError("OPENROUTER_API_KEY environment variable not set")

    for doc in DOCS:
        doc_path = f"{DOCS_DIR}/{doc}"
        if not os.path.exists(doc_path):
            print(f"  SKIP (not found): {doc_path}")
            continue
        base = doc.replace(".pdf", "")
        out_path = f"{GROUND_TRUTH_DIR}/qa_{base}.json"
        if os.path.exists(out_path):
            print(f"  SKIP (already exists): {out_path}")
            continue
        try:
            generate_qa_for_doc(doc_path)
        except Exception as e:
            print(f"  ERROR for {doc}: {e}")

    print("\nGround truth generation complete.")
