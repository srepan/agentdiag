import re
from dataclasses import dataclass

from agentdiag.models import Diagnosis


@dataclass
class EvaluationResult:
    category_correct: bool
    root_cause_correct: bool
    evidence_score: float
    score: float


STOP_WORDS = {
    "a",
    "an",
    "the",
    "is",
    "are",
    "was",
    "were",
    "to",
    "of",
    "and",
    "or",
    "for",
    "in",
    "on",
    "with",
    "has",
    "have",
}


def normalize_label(value: str) -> str:
    return (
        value.strip()
        .lower()
        .replace("-", "_")
        .replace(" ", "_")
    )


def tokenize(value: str) -> set[str]:
    words = re.findall(
        r"[a-z0-9_.]+",
        value.lower(),
    )

    return {
        word
        for word in words
        if word not in STOP_WORDS
    }


def evidence_matches(
    expected: str,
    actual: str,
    threshold: float = 0.6,
) -> bool:
    expected_tokens = tokenize(expected)
    actual_tokens = tokenize(actual)

    if not expected_tokens:
        return False

    overlap = expected_tokens & actual_tokens

    coverage = (
        len(overlap)
        / len(expected_tokens)
    )

    return coverage >= threshold


def evaluate_diagnosis(
    scenario: dict,
    diagnosis: Diagnosis,
) -> EvaluationResult:
    ground_truth = scenario["ground_truth"]

    # Category evaluation
    expected_category = normalize_label(
        ground_truth["category"]
    )

    actual_category = normalize_label(
        diagnosis.category
    )

    category_correct = (
        actual_category == expected_category
    )

    # Root cause evaluation
    expected_root_cause = normalize_label(
        ground_truth["root_cause"]
    )

    accepted_causes = {
        expected_root_cause
    }

    for alias in ground_truth.get(
        "accepted_aliases",
        [],
    ):
        accepted_causes.add(
            normalize_label(alias)
        )

    actual_root_cause = normalize_label(
        diagnosis.root_cause
    )

    root_cause_correct = (
        actual_root_cause
        in accepted_causes
    )

    # Evidence evaluation
    expected_evidence = ground_truth.get(
        "expected_evidence",
        [],
    )

    matched_evidence = 0

    for expected in expected_evidence:
        match_found = any(
            evidence_matches(
                expected,
                actual,
            )
            for actual in diagnosis.evidence
        )

        if match_found:
            matched_evidence += 1

    if expected_evidence:
        evidence_score = (
            matched_evidence
            / len(expected_evidence)
        )
    else:
        evidence_score = 1.0

    # Overall score
    category_score = (
        1.0
        if category_correct
        else 0.0
    )

    root_cause_score = (
        1.0
        if root_cause_correct
        else 0.0
    )

    score = (
        category_score * 0.25
        + root_cause_score * 0.50
        + evidence_score * 0.25
    )

    return EvaluationResult(
        category_correct=category_correct,
        root_cause_correct=root_cause_correct,
        evidence_score=evidence_score,
        score=score,
    )