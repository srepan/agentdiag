# AgentDiag

**A benchmark for evaluating evidence-grounded root-cause diagnosis in AI systems.**

AgentDiag evaluates whether an AI system can diagnose failures from provided incident evidence rather than simply generate plausible troubleshooting responses.

The benchmark presents synthetic incident observations to a diagnostic model, captures a structured diagnosis, and evaluates the response against predefined ground truth that is excluded from the model prompt.

AgentDiag focuses on three questions:

1. Did the model classify the failure correctly?
2. Did the model identify the correct root cause?
3. Did the model ground its diagnosis in the available evidence?

> **Status:** AgentDiag is currently an early experimental release. v0.1 uses a small set of synthetic scenarios and a deterministic evaluator. The benchmark and scoring methodology are expected to evolve.

---

## Why AgentDiag?

AI agents increasingly depend on models, tools, retrieval systems, identity, networking, and orchestration components.

When these systems fail, generating a plausible answer is not enough. A diagnostic system should ideally be able to:

- distinguish symptoms from root causes;
- classify the failure correctly;
- identify the specific underlying cause;
- support the diagnosis with available evidence;
- avoid unsupported conclusions; and
- recommend an appropriate remediation.

AgentDiag v0.1 currently evaluates category accuracy, root-cause accuracy, and deterministic token-based evidence grounding. Remediation and model-reported confidence are captured but are not currently scored.

AgentDiag provides a structured framework for repeatedly evaluating diagnostic-model responses against defined scenarios and deterministic evaluation rules.

Rather than asking only:

> Did the agent complete the task?

AgentDiag asks:

> Can the system correctly diagnose why the task failed using the evidence it was given?

---

## Current capabilities

AgentDiag v0.1 provides:

- JSON-based synthetic incident scenarios
- predefined evaluation ground truth that is not provided to the diagnostic model
- structured LLM diagnostic output
- failure-category evaluation
- root-cause evaluation
- accepted aliases for equivalent root-cause labels
- deterministic token-based evidence-grounding evaluation
- weighted benchmark scoring
- automatic execution of multiple scenarios
- aggregate benchmark results
- automated tests for deterministic evaluator behavior
- support for an Azure-hosted model through Microsoft Entra ID authentication in the current reference implementation

The scenario format is designed to represent synthetic incident observations independently of a specific production incident source.

The initial scenarios are synthetic and contain no production or customer data.

---

## How it works

```text
Synthetic Incident
       |
       v
Scenario Observations
       |
       v
Diagnostic Model
       |
       v
Structured Diagnosis
       |
       +---- Category
       +---- Root Cause
       +---- Confidence
       +---- Evidence
       +---- Remediation
       |
       v
AgentDiag Evaluator <---- Evaluation Ground Truth
       |                 (not provided to model)
       v
Benchmark Score
```

The diagnostic model receives the incident description and observations.

It does **not** receive the scenario's ground truth.

The evaluator compares the resulting structured diagnosis with the predefined ground truth.

---

## Example scenario

A simplified AgentDiag scenario looks like this:

```json
{
  "id": "tool-001",
  "category": "tool_failure",
  "description": "An AI agent fails while calling a weather tool.",
  "observations": [
    "The user's request was successfully received.",
    "The language model successfully selected the weather tool.",
    "The tool expected a parameter named location.",
    "The agent sent a parameter named city.",
    "The tool returned: Missing required parameter: location"
  ],
  "ground_truth": {
    "category": "tool",
    "root_cause": "tool_schema_mismatch",
    "accepted_aliases": [
      "tool_parameter_name_mismatch",
      "parameter_name_mismatch",
      "tool_parameter_mismatch",
      "parameter_schema_mismatch"
    ],
    "expected_evidence": [
      "Tool expected location",
      "Agent provided city"
    ],
    "expected_remediation": "Use the location parameter required by the tool schema."
  }
}
```

Only the incident description and observations are supplied to the diagnostic model.

The `ground_truth` section is used by AgentDiag during evaluation.

---

## Structured diagnosis

AgentDiag asks the diagnostic model to return a structured result containing:

```json
{
  "category": "tool",
  "root_cause": "tool_parameter_name_mismatch",
  "confidence": 0.99,
  "evidence": [
    "The tool expected a parameter named location.",
    "The agent sent a parameter named city.",
    "The tool returned: Missing required parameter: location."
  ],
  "remediation": "Invoke the tool using the required location parameter."
}
```

Separating the broad failure category from the specific root cause helps distinguish two different diagnostic abilities.

For example:

```text
Category:
authorization
Specific root cause:
missing_permission
```

This is more informative than requiring a model to reproduce one exact failure label.

---

## Evaluation

AgentDiag v0.1 evaluates three dimensions.

### 1. Category accuracy

Does the predicted failure category match the expected category?

Example:

```text
Expected: authorization
Predicted: authorization
Result: PASS
```

---

### 2. Root-cause accuracy

Does the predicted root cause match either:

- the canonical root cause; or
- an explicitly accepted equivalent alias?

Example:

```text
Canonical root cause:
tool_schema_mismatch
Accepted equivalent:
tool_parameter_name_mismatch
```

This allows explicitly configured equivalent root-cause labels to be accepted without requiring an exact match to the canonical label.

---

### 3. Evidence grounding

Does the diagnosis reference evidence corresponding to the expected evidence?

The current v0.1 evaluator uses deterministic normalized token matching.

This approach is intentionally simple and deterministic, but it has limitations when evidence is heavily paraphrased.

Semantic evidence evaluation is an area for future work.

---

## Scoring

The current experimental AgentDiag score is:

```text
Category Accuracy       25%
Root-Cause Accuracy     50%
Evidence Grounding      25%
                       ----
Overall Score           100%
```

These weights are an **experimental design choice for AgentDiag v0.1**. They are not an industry standard.

The scoring methodology may change as the benchmark develops.

Model-reported confidence is captured but is not currently included in the v0.1 overall score.

Remediation is also captured but is not currently scored.

---

## Current scenario coverage

The initial benchmark contains synthetic scenarios covering:

### Tool failure

An agent invokes a tool using an incorrect argument name.

The benchmark evaluates whether the diagnostic model identifies the tool-interface or parameter mismatch.

### Authorization failure

Authentication succeeds, but the identity does not possess a permission required by the downstream resource.

The benchmark evaluates whether the diagnostic model distinguishes authorization failure from authentication failure.

Additional failure categories are planned for future releases.

---

## Example benchmark output

An illustrative benchmark result is shown below. Actual output and scores depend on the diagnostic model response and evaluator results:

```text
AgentDiag Benchmark
============================================================

Running: identity-001
Category: authorization
------------------------------------------------------------

Agent Diagnosis
------------------------------------------------------------
Predicted Category: authorization
Root Cause: missing_documents_read_permission
Confidence: 99%

Evidence:
 - The access token is valid and has not expired.
 - The document service returned HTTP 403 Forbidden.
 - The agent identity does not have the documents.read permission.

Remediation:
Grant the required permission and retry the request.

Evaluation
------------------------------------------------------------
Category: PASS
Root Cause: PASS
Evidence Grounding: 100%
Overall Score: 100%
```

Results depend on the diagnostic model and the evidence returned for each scenario.

---

## Project structure

```text
agentdiag/
|
+-- agentdiag/
|   +-- __init__.py
|   +-- agents.py
|   +-- evaluator.py
|   +-- llm_agent.py
|   +-- models.py
|   +-- runner.py
|
+-- scenarios/
|   +-- authorization_failure.json
|   +-- tool_failure.json
|
+-- tests/
|   +-- test_evaluator.py
|
+-- .gitignore
+-- README.md
+-- requirements.txt
```

Local configuration can be stored in .env. The .env file must not be committed to source control.

---

## Requirements

The current reference implementation requires:

- Python
- access to a compatible model endpoint
- Python dependencies listed in `requirements.txt`

The current development and test environment uses Python 3.14.2. Support for other Python versions has not yet been validated.

The current development implementation uses an Azure-hosted model with Microsoft Entra ID authentication.

---

## Installation

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd agentdiag
```

Create a Python virtual environment.

### Windows

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## Configuration

The current reference implementation has been tested with an Azure-hosted model using Microsoft Entra ID authentication.

Create a local `.env` file containing the endpoint and deployment configuration:

```text
AZURE_OPENAI_ENDPOINT=YOUR_MODEL_ENDPOINT
AZURE_OPENAI_DEPLOYMENT=YOUR_DEPLOYMENT_NAME
```

Do not commit credentials, tokens, or environment-specific secrets.

### Authentication

Before running the benchmark, authenticate with an Azure identity that has access to the configured model endpoint:

```powershell
az login
```

If the model resource belongs to a specific Microsoft Entra tenant, authenticate explicitly against that tenant:

```powershell
az login --tenant YOUR_TENANT_ID
```

Then run the benchmark:

```powershell
python -m agentdiag.runner
```

> Authentication and endpoint configuration can vary by deployment. AgentDiag does not require scenario files to contain authentication secrets.

---
## Run the benchmark

From the repository root:

```powershell
python -m agentdiag.runner
```

AgentDiag automatically discovers JSON scenario files under:

```text
scenarios/
```

Each scenario's incident description and observations are sent to the diagnostic model. The resulting diagnosis is then evaluated against the scenario's predefined ground truth, which is not included in the model prompt.

A benchmark summary is displayed after all successfully evaluated scenarios complete.

---

## Run the tests

AgentDiag includes automated tests for the deterministic evaluator.

Run:

```powershell
python -m pytest -v
```

The current tests validate:

- label normalization
- exact root-cause matching
- accepted root-cause aliases
- incorrect category detection
- incorrect root-cause detection
- related evidence matching
- unrelated evidence rejection
- perfect-score evaluation

---

## Design principles

### Ground truth must remain separate from diagnosis

The model should receive observations, not the expected answer.

This separation is fundamental to meaningful diagnostic evaluation.

### Diagnosis should be evidence-grounded

A correct root-cause label without supporting evidence is less useful than a diagnosis that demonstrates why the conclusion follows from the available observations.

### Evaluation should be reproducible

AgentDiag v0.1 favors deterministic evaluation mechanisms where practical.

### Scenarios should be safe to share

The initial benchmark uses synthetic incidents.

Scenario contributions should not contain:

- customer information
- credentials
- proprietary production telemetry
- confidential incident data
- personal data
- secrets or tokens

### Model integration should remain extensible

AgentDiag's architecture is intended to allow additional model-provider and diagnostic-agent integrations in future releases.

The current Azure-hosted integration is the reference implementation tested for v0.1.

---

## Limitations

AgentDiag v0.1 is intentionally small.

Current limitations include:

- only a small number of synthetic scenarios;
- deterministic token-based rather than semantic evidence matching;
- manually defined root-cause aliases;
- remediation quality is captured but not scored;
- model confidence is captured but calibration is not evaluated;
- unsupported-claim detection is not currently implemented;
- the benchmark does not reproduce or inject real infrastructure failures;
- only the current Azure-hosted reference model integration has been tested;
- scoring weights are experimental and have not been empirically calibrated;
- support across multiple Python versions has not yet been validated.

These limitations are intended to be explicit areas for future experimentation and evaluation.

## What AgentDiag does not claim

AgentDiag v0.1 does not claim to:
 
- measure general model intelligence;
- prove that a model or agent is production-ready or safe;
- reproduce real infrastructure failures;
- perform semantic equivalence evaluation;
- validate arbitrary real-world diagnoses;
- measure remediation quality;
- measure hallucination or unsupported-claim rates;
- provide a comprehensive taxonomy of AI-agent failures.
 
AgentDiag scores should be interpreted only within the scenario corpus, taxonomy, scoring weights, and evaluation rules of the benchmark version being executed.

---
## Roadmap

Potential areas for future development include:

- additional synthetic failure scenarios;
- broader failure-category coverage;
- semantic evidence-grounding evaluation;
- remediation-quality evaluation;
- unsupported-claim detection;
- additional model-provider integrations;
- validation across additional Python versions;
- comparison of multiple diagnostic models using the same scenario corpus;
- controlled fault-injection scenarios for selected failure types.

## License

No open-source license has been applied to AgentDiag v0.1. The source code is publicly available for viewing, but no additional rights to use, modify, or distribute the code are granted by this repository.