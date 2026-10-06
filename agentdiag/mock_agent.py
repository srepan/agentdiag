from agentdiag.agents import DiagnosticAgent
from agentdiag.models import Diagnosis


class MockDiagnosticAgent(DiagnosticAgent):

    def diagnose(self, scenario: dict) -> Diagnosis:

        return Diagnosis(
            root_cause="tool_schema_mismatch",
            confidence=0.95,
            evidence=[
                "Tool expected location",
                "Agent provided city"
            ],
            remediation=(
                "Use the location parameter required "
                "by the tool schema."
            )
        )