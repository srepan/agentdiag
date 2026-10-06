from abc import ABC, abstractmethod

from agentdiag.models import Diagnosis


class DiagnosticAgent(ABC):

    @abstractmethod
    def diagnose(self, scenario: dict) -> Diagnosis:
        """
        Analyze an incident scenario and return a structured diagnosis.
        """
        pass