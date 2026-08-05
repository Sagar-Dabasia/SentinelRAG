# Evaluation Plan

## Research Questions
* **Baseline security vulnerability:** What is the baseline susceptibility of the RAG implementation to prompt injection and context poisoning?
* **Mitigation effectiveness:** How effectively do layered controls reduce the success rate of attacks?
* **Utility trade-off:** What is the impact of security controls on normal request utility, latency, and false-refusal rates?
* **Operational cost:** How do defensive mitigations affect context-window usage and token costs?
* **Later model sensitivity:** How do different foundational models compare in inherent resilience and susceptibility?

## Initial Hypotheses
* *Provisional:* Baseline indirect injection success will be materially greater than zero.
* *Provisional:* Server-side retrieval authorization should produce zero cross-user retrieval in maintained regression cases.
* *Provisional:* Layered controls should reduce attack success.
* *Provisional:* Security controls may increase latency and false refusals.
* *Provisional:* Model comparison is deferred until the evaluation pipeline is stable.

## Controlled Baseline (Reduced-Defence)
* **Label:** `LAB_ONLY`
* **State:** Disabled by default.
* **Requirement:** Explicit configuration flag required to enable.
* **Constraints:** Synthetic data only, local environment only, no public deployment.
* **Security invariant:** No weakened authentication, no OS or general-purpose application vulnerability.
* **Safety constraint:** CI must not expose a live service; tests must prove the default configuration cannot enable it accidentally.
* **Purpose:** Limited strictly to comparing AI/RAG-layer controls by providing a completely unmitigated AI baseline.

## Dataset Plan

### Schemas and Manifests
Every dataset manifest must record:
* Name
* Version
* Source or generation method
* Licence
* File list
* Row or case count
* Cryptographic digest
* Permitted use

### Normal Utility Dataset
* **Case ID:** Unique identifier
* **Dataset version:** Link to manifest
* **User or tenant identity:** Synthetic tenant ID
* **Documents required:** List of background context files
* **Query:** Benign user input
* **Expected authorized documents:** Ground truth retrieval
* **Expected citations:** Required source chunks
* **Deterministic success criteria:** Exact match or regex on expected facts

### Direct Attack Dataset
* **Case ID:** Unique identifier
* **Category:** e.g., System-prompt extraction
* **Query or attack input:** Malicious prompt payload
* **Expected refusal state:** System should safely refuse or deflect
* **Deterministic success criteria:** Absence of leaked canary/prompt

### Indirect Attack Dataset
* **Case ID:** Unique identifier
* **Category:** e.g., Retrieval poisoning
* **Documents required:** Malicious documents seeded in store
* **Query:** Benign trigger query
* **Expected canary state:** Leakage of canary string
* **Framework mapping:** E.g., LLM01:2026

## Metrics
* **Retrieval recall at K:** (Relevant documents retrieved) / (Total relevant documents in set)
* **Unauthorized retrieval rate:** (Unauthorized chunks retrieved) / (Total chunks retrieved)
* **Cross-user leakage rate:** (Responses containing cross-user canaries) / (Total responses evaluated)
* **Canary leakage rate:** (Responses containing target canary) / (Total responses evaluated)
* **Citation support correctness:** (Citations factually supporting generation) / (Total citations provided)
* **Correct abstention:** (Requests safely refused when appropriate) / (Total out-of-bounds requests)
* **Normal-request success:** (Benign requests successfully fulfilled) / (Total benign requests)
* **Attack success rate:** (Successful exploits) / (Total attack attempts)
* **Indirect-injection success:** (Payloads successfully executed via retrieval) / (Total seeded payloads retrieved)
* **System-prompt leakage:** (Responses containing system prompt segments) / (Total extraction attempts)
* **False-positive rate:** (Benign requests blocked) / (Total benign requests)
* **False-refusal rate:** (Benign requests refused by generation) / (Total benign requests)
* **Latency:** End-to-end response time (milliseconds)
* **Memory use:** Peak memory footprint (where practical)
* **Token or context usage:** Input/output tokens consumed per request
* **Utility change before/after defence:** (Normal-request success with defence) - (Normal-request success without defence)
* **Latency change before/after defence:** (Latency with defence) - (Latency without defence)

## Experiment Metadata
Format: JSON / JSONL.
Required fields:
* `run_id`: Unique run identifier
* `utc_timestamp`: Execution time
* `git_commit`: Exact source version
* `branch`: Current git branch
* `dirty_tree`: Boolean flag for uncommitted changes
* `application_version`: Semantic version
* `configuration_digest`: Hash of active config
* `dataset_manifest`, `dataset_digest`: Dataset provenance
* `attack_set_version`: Attack suite provenance
* `model_provider`, `model_identifier`, `model_parameters`: Model details
* `embedding_model`, `embedding_configuration`: Embedding details
* `prompt_template_version`: Template identifier
* `retrieval_parameters`: Top-K, thresholds
* `defence_configuration`: Active mitigations and flags
* `random_seed`: For reproducibility
* `hardware_summary`: Environment constraints (e.g. RTX 4060)
* `start_timestamp`, `end_timestamp`: Duration bounds
* `latency`: Measured delay
* `metric_values`: Key-value map of calculated metrics
* `errors`: Any runtime exceptions
* `outcome`: Overall run status

## Procedure
1. Validate repository and configuration state.
2. Validate dataset manifest and digest.
3. Start local services.
4. Reset controlled test state.
5. Load synthetic tenants and canaries.
6. Execute normal utility cases.
7. Execute attack cases.
8. Apply deterministic judgments first.
9. Apply human judgment where required.
10. Apply calibrated LLM judgment only when necessary.
11. Write immutable run metadata.
12. Generate summaries from raw results.
13. Compare baseline and defence runs.
14. Preserve failures and invalid runs.

## Analysis
* **Descriptive statistics:** Central tendencies and variances.
* **Per-attack-category results:** Drill-downs by threat vector.
* **Per-model results:** Deferred until later phases.
* **Confidence intervals:** Applied only where sample size and method justify them.
* **No false significance claims:** Avoid overstating conclusions from tiny curated datasets.
* **Before/after changes:** Absolute and percentage-point shifts.
* **Manual review:** Human verification of critical failures.
* **Invalid-run rules:** Defined conditions that discard a run (e.g. config drift).
* **No averaging away:** Cross-user leakage is a critical binary failure and must not be averaged away.

## Threats to Validity
* **Small curated datasets:** May not generalize to real-world variance.
* **Model sensitivity:** Variations between LLM providers or updates.
* **Prompt-template sensitivity:** Fragility of specific phrasing.
* **Hardware effects:** Quantization or timing changes due to local constraints.
* **Stochastic generation:** Inherent non-determinism in LLMs.
* **Dataset contamination:** Risk of evaluating on data seen in pre-training.
* **Human-label inconsistency:** Variance in manual judgments.
* **LLM-judge bias:** Evaluator models favoring specific styles or their own outputs.
* **Overfitting mitigations to known attacks:** Defences that fail against novel variations.
* **Synthetic-data limitations:** Lack of real-world noise and complexity.
* **Local-model generalizability:** Findings on 8GB models may not perfectly map to frontier models.
* **Framework mapping subjectivity:** Inherent ambiguity in categorizing complex attacks.
