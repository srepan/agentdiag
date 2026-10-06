import json
from pathlib import Path

from agentdiag.llm_agent import LLMDiagnosticAgent
from agentdiag.evaluator import evaluate_diagnosis


def load_scenario(path: Path) -> dict:
    """
    Load a single AgentDiag scenario from a JSON file.
    """
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    """
    Run all AgentDiag benchmark scenarios found in the
    scenarios directory.
    """

    scenarios_dir = Path("scenarios")

    # Find all JSON scenario files.
    scenario_files = sorted(
        scenarios_dir.glob("*.json")
    )

    if not scenario_files:
        print("No scenarios found in the scenarios directory.")
        return

    # Create the diagnostic agent once and reuse it
    # for all benchmark scenarios.
    agent = LLMDiagnosticAgent()

    # Benchmark totals.
    total_scenarios = 0
    category_passes = 0
    root_cause_passes = 0
    total_evidence_score = 0.0
    total_score = 0.0

    print()
    print("AgentDiag Benchmark")
    print("=" * 60)

    # Run every scenario.
    for scenario_file in scenario_files:

        print()

        try:
            scenario = load_scenario(scenario_file)

            print(f"Running: {scenario['id']}")
            print(f"Category: {scenario['category']}")
            print("-" * 60)

            # Ask the LLM diagnostic agent to diagnose
            # the incident.
            diagnosis = agent.diagnose(scenario)

            # Evaluate the diagnosis against the
            # benchmark ground truth.
            evaluation = evaluate_diagnosis(
                scenario,
                diagnosis
            )

            if evaluation.root_cause_correct:
                status = "PASS"
            else:
                status = "FAIL"

            # Display diagnosis.
            print()
            print("Agent Diagnosis")
            print("-" * 60)

            print(
                f"Predicted Category: "
                f"{diagnosis.category}"
            )
            print(
                f"Root Cause: "
                f"{diagnosis.root_cause}"
            )

            print(
                f"Confidence: "
                f"{diagnosis.confidence:.0%}"
            )

            print()
            print("Evidence:")

            for evidence in diagnosis.evidence:
                print(f" - {evidence}")

            print()
            print(
                f"Remediation: "
                f"{diagnosis.remediation}"
            )

            # Display scenario evaluation.
            print()
            print("Evaluation")
            print("-" * 60)

            category_status = (
                "PASS"
                if evaluation.category_correct
                    else "FAIL"
            )

            root_cause_status = (
                "PASS"
                if evaluation.root_cause_correct
                    else "FAIL"
            )

            print(
                f"Category: "
                f"{category_status}"
            )

            print(
                f"Root Cause: "
                f"{root_cause_status}"
            )

            print(
                f"Evidence Grounding: "
                f"{evaluation.evidence_score:.0%}"
            )

            print(
                f"Overall Score: "
                f"{evaluation.score:.0%}"
            )

            # Update benchmark totals.
            total_scenarios += 1

            if evaluation.category_correct:
                category_passes += 1

            if evaluation.root_cause_correct:
                root_cause_passes += 1

            total_evidence_score += (
                evaluation.evidence_score
            )

            total_score += (
                evaluation.score
            )

        except Exception as error:

            print(
                f"Scenario file: "
                f"{scenario_file.name}"
            )

            print("Status: ERROR")
            print(f"Error: {error}")

    # -------------------------------------------------
    # Benchmark Summary
    # -------------------------------------------------

    print()
    print("=" * 60)
    print("Benchmark Summary")
    print("=" * 60)

    if total_scenarios == 0:
        print(
            "No scenarios were successfully evaluated."
        )
        return

    root_cause_accuracy = (
        root_cause_passes /
        total_scenarios
    )

    category_accuracy = (
    category_passes /
    total_scenarios
)
    average_evidence_score = (
        total_evidence_score /
        total_scenarios
    )

    average_score = (
        total_score /
        total_scenarios
    )

    print(
        f"Scenarios Evaluated: "
        f"{total_scenarios}"
    )

    print(
        f"Root Cause Accuracy: "
        f"{root_cause_passes}/"
        f"{total_scenarios} "
        f"({root_cause_accuracy:.0%})"
    )

    print(
        f"Category Accuracy: "
        f"{category_passes}/"
        f"{total_scenarios} "
        f"({category_accuracy:.0%})"
    )

    print(
        f"Average Evidence Grounding: "
        f"{average_evidence_score:.0%}"
    )

    print(
        f"Overall AgentDiag Score: "
        f"{average_score:.0%}"
    )


if __name__ == "__main__":
    main()