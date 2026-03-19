import math
import numpy as np
from typing import List


def recall_at_k(retrieved: List[int], relevant: List[int], k: int = 5) -> float:
    if not relevant:
        return 0.0
    return len(set(retrieved[:k]) & set(relevant)) / len(set(relevant))


def mean_reciprocal_rank(retrieved: List[int], relevant: List[int]) -> float:
    relevant_set = set(relevant)
    for rank, rid in enumerate(retrieved, 1):
        if rid in relevant_set:
            return 1.0 / rank
    return 0.0


def ndcg_at_k(retrieved: List[int], relevant: List[int], k: int = 5) -> float:
    relevant_set = set(relevant)
    gains = [1 if rid in relevant_set else 0 for rid in retrieved[:k]]

    def dcg(vals):
        return sum(val / math.log2(i + 2) for i, val in enumerate(vals))

    idcg = dcg(sorted(gains, reverse=True))
    return 0.0 if idcg == 0 else dcg(gains) / idcg


def answer_similarity_score(answer_emb: List[float],
                            chunk_embeddings: List[List[float]]) -> float:
    """Average cosine similarity (top-3) between the expected-answer embedding
    and retrieved chunk embeddings.

    Uses the same model that is being evaluated, so the score reflects how well
    that model maps answers and their supporting chunks into nearby vector space.
    Returns 0.0 if either input is empty.
    """
    if not answer_emb or not chunk_embeddings:
        return 0.0

    a = np.array(answer_emb, dtype=np.float32)
    a_norm = np.linalg.norm(a)
    if a_norm == 0:
        return 0.0

    sims = []
    for chunk_emb in chunk_embeddings:
        c = np.array(chunk_emb, dtype=np.float32)
        c_norm = np.linalg.norm(c)
        if c_norm > 0:
            sims.append(float(np.dot(a, c) / (a_norm * c_norm)))

    if not sims:
        return 0.0

    top3 = sorted(sims, reverse=True)[:3]
    return round(sum(top3) / len(top3), 4)


def composite_score(recall: float, mrr: float, ndcg: float, ans_sim: float) -> float:
    """Weighted composite score for RAG evaluation.

    Weights: ans_sim=30%, recall=30%, ndcg=25%, mrr=15%
    - ans_sim  measures semantic proximity of retrieved content to the correct answer
    - recall   measures whether the relevant chunk was retrieved at all
    - ndcg     measures ranking quality
    - mrr      measures rank of first relevant result
    """
    return round(ans_sim * 0.30 + recall * 0.30 + ndcg * 0.25 + mrr * 0.15, 4)
