# Evaluation Plan

## Research Questions
Refer to [RESEARCH_QUESTIONS.md](RESEARCH_QUESTIONS.md) for the key questions driving this evaluation.

## Baselines
* **Proposed Baselines:** A completely undefended, naive RAG pipeline with standard parameters.

## Planned Datasets (Future Work)
* Normal query datasets (for utility testing).
* Direct-attack datasets (for testing injection resistance).
* Indirect-attack datasets (for testing retrieval poisoning and hidden instruction execution).

## Checks & Metrics
* **Planned deterministic checks:** Exact matching for synthetic canary leakage and fixed format violations.
* **Planned human-labelled checks:** Manual verification for edge cases and utility nuances.
* **LLM Judging:** Limited use of LLM-as-a-judge to evaluate generation quality, with strict awareness of bias.
* **Metrics:** Security (exploit success rate), Utility (answer correctness, helpfulness), and Trade-off (latency, overhead).

## Methodology
* **Canary Leakage Testing:** Will inject synthetic secrets into context to verify if the model leaks them.
* **Experiment Metadata:** Every evaluation run must record the exact prompt template, model version, dataset version, and parameters used.
* **Threats to Validity:** We acknowledge that local models may not generalize to state-of-the-art hosted models. Mitigations will be tested primarily for their conceptual validity.
* **Reproducibility:** All evaluations must be reproducible from a fresh local environment.
* **Honest Reporting:** No fabricated target achievements. Dataset construction and evaluation implementation are future work.
