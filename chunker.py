import re
from typing import List

import tiktoken

# These defaults mirror the Go implementation.
DEFAULT_TOKEN_LIMIT = 500
DEFAULT_OVERLAP = 50
OPENAI_ENCODING = "cl100k_base"

_encoding = None


def _get_encoding():
    global _encoding
    if _encoding is None:
        _encoding = tiktoken.get_encoding(OPENAI_ENCODING)
    return _encoding


def _count_tokens(s: str) -> int:
    if not s:
        return 0
    return len(_get_encoding().encode(s))


# Port of the Go regex:
# `[.?!。？！\s]*[\n]+[.?!。？！\s]*|[.?!。？！]+[\s]*`
_sentence_end_re = re.compile(r"[.?!。？！\s]*[\n]+[.?!。？！\s]*|[.?!。？！]+[\s]*")


def _split_sentences(text: str) -> List[str]:
    matches = list(_sentence_end_re.finditer(text))
    sentences: List[str] = []
    last_index = 0

    for m in matches:
        part = text[last_index : m.end()]
        part = part.strip()
        if part:
            sentences.append(part)
        last_index = m.end()

    if last_index < len(text):
        part = text[last_index:]
        part = part.strip()
        if part:
            sentences.append(part)

    return sentences


def _segments_from_sentences(sentences: List[str], token_limit: int) -> List[str]:
    enc = _get_encoding()
    out: List[str] = []

    for s in sentences:
        tokens = enc.encode(s)
        if len(tokens) <= token_limit:
            out.append(s)
            continue
        out.extend(_split_tokens_to_segments(enc, tokens, token_limit))

    return out


def _split_tokens_to_segments(enc, tokens, token_limit: int) -> List[str]:
    segments: List[str] = []
    for start in range(0, len(tokens), token_limit):
        end = min(start + token_limit, len(tokens))
        segments.append(enc.decode(tokens[start:end]))
    return segments


def _chunk_segments_by_tokens(
    segments: List[str], token_limit: int, overlap_tokens: int
) -> List[List[str]]:
    chunks: List[List[str]] = []
    current: List[str] = []
    current_tokens = 0

    overlap_segs: List[str] = []
    overlap_count = 0

    for seg in segments:
        n = _count_tokens(seg)
        if current and current_tokens + n > token_limit:
            # Finalize current chunk.
            chunks.append(list(current))

            # Build overlap from the end of current.
            overlap_segs = []
            overlap_count = 0
            for i in range(len(current) - 1, -1, -1):
                if overlap_count >= overlap_tokens:
                    break
                overlap_segs.insert(0, current[i])
                overlap_count += _count_tokens(current[i])

            current = list(overlap_segs)
            current_tokens = overlap_count

        current.append(seg)
        current_tokens += n

    if current:
        chunks.append(current)

    return chunks


def chunk_documents(document: str, tokens: int, overlap: int) -> List[str]:
    """
    Python port of the Go ChunkDocuments:
    - Trims input
    - Uses sentence-based segmentation with token-aware splitting
    - Applies overlapping chunks in token space
    """
    doc = document.strip()
    if not doc:
        return []

    if tokens <= 0:
        tokens = DEFAULT_TOKEN_LIMIT
    if overlap < 0:
        overlap = DEFAULT_OVERLAP
    if overlap >= tokens:
        overlap = tokens - 1

    sentences = _split_sentences(doc)
    if not sentences:
        return []

    segments = _segments_from_sentences(sentences, tokens)
    if not segments:
        return []

    raw_chunks = _chunk_segments_by_tokens(segments, tokens, overlap)
    return [" ".join(chunk) for chunk in raw_chunks]


def get_chunks(text: str, strategy_name: str, config: dict) -> List[str]:
    """
    Main entrypoint used by the rest of the codebase.

    For method == "token", this now mirrors the Go ChunkDocuments implementation.
    """
    method = config["method"]

    if method == "token":
        size = config.get("size", DEFAULT_TOKEN_LIMIT)
        overlap = config.get("overlap", DEFAULT_OVERLAP)
        return chunk_documents(text, size, overlap)

    # Keep the other strategies for backwards compatibility if they are used anywhere.
    if method == "sentence":
        # Sentence mode: just return raw sentence splits with default token limit.
        sentences = _split_sentences(text)
        return sentences

    if method == "sliding":
        # Approximate a sliding window using ChunkDocuments by controlling overlap.
        size = config.get("size", DEFAULT_TOKEN_LIMIT)
        stride = config.get("stride", size // 2)
        # overlap in tokens ≈ size - stride
        overlap = max(0, size - stride)
        return chunk_documents(text, size, overlap)

    raise ValueError(f"Unknown chunking method: {method}")
