import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from azure.identity import (
    DefaultAzureCredential,
    get_bearer_token_provider,
)

from agentdiag.agents import DiagnosticAgent
from agentdiag.models import Diagnosis


load_dotenv()


class LLMDiagnosticAgent(DiagnosticAgent):

    def __init__(self):

        token_provider = get_bearer_token_provider(
            DefaultAzureCredential(),
            "https://ai.azure.com/.default"
        )

        self.client = OpenAI(
            base_url=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=token_provider,
        )

        self.deployment = os.environ[
            "AZURE_OPENAI_DEPLOYMENT"
        ]

    def diagnose(self, scenario: dict) -> Diagnosis:

        observations = "\n".join(
            f"- {item}"
            for item in scenario["observations"]
        )

        prompt = f"""
You are diagnosing a failure in an AI agent system.

Analyze ONLY the evidence provided below.

Incident:
{scenario["description"]}

Observations:
{observations}

Return JSON only using this structure:

{{
  "category": "failure_category",
  "root_cause": "specific_machine_readable_root_cause",
  "confidence": 0.0,
  "evidence": [
    "evidence item"
  ],
  "remediation": "recommended remediation"
}}

Allowed categories:
- authentication
- authorization
- tool
- network
- retrieval
- model
- orchestration

Rules:
- Base the diagnosis only on supplied evidence.
- Do not invent observations.
- category must be one of the allowed categories above.
- root_cause must be a short machine-readable label.
- Use lowercase snake_case for root_cause.
- Do not put sentences or explanations in root_cause.
- Put explanation and supporting facts in evidence.
- confidence must be between 0 and 1.
"""

        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format={
                "type": "json_object"
            },
        )

        result = json.loads(
            response.choices[0].message.content
        )

        return Diagnosis(
            category=result["category"],
            root_cause=result["root_cause"],
            confidence=float(result["confidence"]),
            evidence=result["evidence"],
            remediation=result["remediation"],
        )