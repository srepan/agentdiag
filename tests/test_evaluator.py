from agentdiag.evaluator import (
    evidence_matches,
    evaluate_diagnosis,
    normalize_label,
)
from agentdiag.models import Diagnosis


def make_scenario():
    return {
        "id": "test-001",
        "category": "authorization",
        "description": "Test scenario",
        "observations": [
            "The access token is valid.",
            "The identity does not have documents.read permission.",
        ],
        "ground_truth": {
            "category": "authorization",
            "root_cause": "missing_permission",
            "accepted_aliases": [
                "permission_missing",
                "missing_documents_read_permission",
            ],
            "expected_evidence": [
                "Access token is valid",
                "documents.read permission is missing",
            ],
            "expected_remediation": (
                "Grant documents.read permission."
            ),
        },
    }


def test_normalize_label():
    result = normalize_label(
        "Missing-Permission"
    )

    assert result == "missing_permission"


def test_root_cause_exact_match():
    scenario = make_scenario()

    diagnosis = Diagnosis(
        category="authorization",
        root_cause="missing_permission",
        confidence=0.95,
        evidence=[
            "The access token is valid.",
            "The documents.read permission is missing.",
        ],
        remediation="Grant documents.read permission.",
    )

    result = evaluate_diagnosis(
        scenario,
        diagnosis,
    )

    assert result.category_correct is True
    assert result.root_cause_correct is True


def test_root_cause_alias_match():
    scenario = make_scenario()

    diagnosis = Diagnosis(
        category="authorization",
        root_cause="missing_documents_read_permission",
        confidence=0.95,
        evidence=[
            "The access token is valid.",
            "The documents.read permission is missing.",
        ],
        remediation="Grant documents.read permission.",
    )

    result = evaluate_diagnosis(
        scenario,
        diagnosis,
    )

    assert result.root_cause_correct is True


def test_wrong_category():
    scenario = make_scenario()

    diagnosis = Diagnosis(
        category="authentication",
        root_cause="missing_permission",
        confidence=0.95,
        evidence=[
            "The access token is valid.",
            "The documents.read permission is missing.",
        ],
        remediation="Grant documents.read permission.",
    )

    result = evaluate_diagnosis(
        scenario,
        diagnosis,
    )

    assert result.category_correct is False
    assert result.root_cause_correct is True


def test_wrong_root_cause():
    scenario = make_scenario()

    diagnosis = Diagnosis(
        category="authorization",
        root_cause="dns_failure",
        confidence=0.90,
        evidence=[
            "The access token is valid.",
        ],
        remediation="Check DNS.",
    )

    result = evaluate_diagnosis(
        scenario,
        diagnosis,
    )

    assert result.root_cause_correct is False


def test_evidence_exact_meaning():
    result = evidence_matches(
        "Access token is valid",
        "The access token is valid and has not expired.",
    )

    assert result is True


def test_evidence_not_related():
    result = evidence_matches(
        "Access token is valid",
        "The DNS lookup failed.",
    )

    assert result is False


def test_perfect_evaluation():
    scenario = make_scenario()

    diagnosis = Diagnosis(
        category="authorization",
        root_cause="missing_permission",
        confidence=0.99,
        evidence=[
            "The access token is valid.",
            "The documents.read permission is missing.",
        ],
        remediation="Grant documents.read permission.",
    )

    result = evaluate_diagnosis(
        scenario,
        diagnosis,
    )

    assert result.category_correct is True
    assert result.root_cause_correct is True
    assert result.evidence_score == 1.0
    assert result.score == 1.0