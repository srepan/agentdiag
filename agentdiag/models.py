from dataclasses import dataclass, field


@dataclass
class Diagnosis:
    category: str
    root_cause: str
    confidence: float
    evidence: list[str] = field(default_factory=list)
    remediation: str = ""