"""Weighted confidence score (0-100) for a RAG chat answer, per
docs/TECHNICAL_REPORT.md: OCR quality (25%) + retrieval quality (25%) +
rule consistency (25%) + answer completeness (25%)."""


def score_ocr_quality(avg_ocr_quality: float | None) -> float:
    if avg_ocr_quality is None:
        return 0.5
    return max(0.0, min(1.0, avg_ocr_quality))


def score_retrieval(hits: list[dict]) -> float:
    if not hits:
        return 0.0
    avg_similarity = sum(h["similarity"] for h in hits) / len(hits)
    count_factor = min(len(hits) / 3, 1.0)
    return max(0.0, min(1.0, 0.7 * avg_similarity + 0.3 * count_factor))


def score_rule_consistency(has_unresolved_conflicting_alerts: bool) -> float:
    return 0.5 if has_unresolved_conflicting_alerts else 1.0


def score_answer_completeness(answer: str) -> float:
    """Cheap proxy for "answer completeness" without a second LLM call: an
    answer that explicitly says it doesn't know / has no evidence is a
    complete-but-empty answer, scored lower than a substantive one."""
    lowered = answer.lower()
    hedge_phrases = ("i don't have", "not in the", "no information", "cannot find", "isn't in your records")
    if any(p in lowered for p in hedge_phrases):
        return 0.5
    return 1.0 if len(answer.strip()) > 20 else 0.6


def compute_confidence(
    avg_ocr_quality: float | None,
    hits: list[dict],
    has_unresolved_conflicting_alerts: bool,
    answer: str,
) -> int:
    weighted = 0.25 * (
        score_ocr_quality(avg_ocr_quality)
        + score_retrieval(hits)
        + score_rule_consistency(has_unresolved_conflicting_alerts)
        + score_answer_completeness(answer)
    )
    return round(max(0.0, min(1.0, weighted)) * 100)
