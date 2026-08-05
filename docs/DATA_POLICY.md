# Data Policy

## Permitted Data
Only synthetic data and publicly licensed datasets may be used in this repository.

## Prohibited Data
The following data is strictly prohibited:
* Confidential data
* Customer or employer data
* Real personal records or PII
* Passwords, API keys, and credentials
* Live service credentials
* Real attack targets

## Data Management
* **Synthetic Canaries:** When required, synthetic canaries will be used for testing leakage.
* **Manifests and Versions:** Datasets must be tracked via manifests and versioned appropriately.
* **Cryptographic Digests:** Where practical, use cryptographic digests to verify dataset integrity.
* **License and Source Recording:** Every external dataset must have its license and source clearly recorded.
* **Retention and Deletion:** Temporary data should be deleted after tests. Retention is limited to the life of the research iteration.
* **Logging Restrictions:** No sensitive query information should be logged in a way that risks exposure.

## Large-Artifact Handling & Git Exclusions
* Large datasets, vector indexes, and generated artifacts must be excluded from Git using `.gitignore`.
* Only small schemas and metadata are permitted in the repository.

## Evaluation-Data Separation
* Evaluation data must be kept separate from training/ingestion data to prevent contamination.

## Prohibited Actions
* No testing against public endpoints without explicit authorization.
