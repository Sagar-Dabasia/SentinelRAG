# Risk Register

| ID | Description | Category | Likelihood | Impact | Severity | Mitigation | Owner | Status | Evidence |
|---|---|---|---|---|---|---|---|---|---|
| RSK-001 | Scope creep | Project | High | Medium | High | Strict adherence to Phase definitions and explicit non-goals. | Project maintainer | Open | - |
| RSK-002 | False security claims | Security | Low | High | High | Use "PLANNED" and "NOT VERIFIED" statuses. Honest prototype positioning. | Project maintainer | Open | - |
| RSK-003 | Cross-user data leakage in later phases | Security | Medium | High | High | Strict data policy, synthetic data only, no real users. | Project maintainer | Open | - |
| RSK-004 | Prompt injection | Security | High | High | High | Layered mitigations to be implemented and evaluated in later phases. | Project maintainer | Open | - |
| RSK-005 | Unsafe ingestion | Security | Medium | High | High | Input validation and format restriction during data loading (Planned). | Project maintainer | Open | - |
| RSK-006 | Dependency compromise | Security | Low | High | Medium | Use `uv.lock`, dependabot, `pip-audit`, and pinned pre-commit hooks. | Project maintainer | Open | - |
| RSK-007 | Secret exposure | Security | Low | High | High | No API keys used. Pre-commit secret scanning, `detect-secrets`. | Project maintainer | Open | - |
| RSK-008 | Local model provenance and licence uncertainty | Legal | Medium | Medium | Medium | Document exact model sources and licenses. | Project maintainer | Open | - |
| RSK-009 | Evaluation contamination | Research | Medium | Medium | Medium | Strict separation of test/train datasets. | Project maintainer | Open | - |
| RSK-010 | LLM-as-judge bias | Research | High | Medium | Medium | Use deterministic checks where possible. Acknowledge bias. | Project maintainer | Open | - |
| RSK-011 | Hardware limits | Technical | High | Low | Low | Design for local-first modular monolith, defer heavy components. | Project maintainer | Open | - |
| RSK-012 | Reproducibility failure | Technical | Medium | High | High | Enforce `uv lock`, explicit instructions, and automated CI tests. | Project maintainer | Open | - |
| RSK-013 | Documentation drifting from implementation | Project | High | Medium | Medium | Strict PR review requirements to update docs with code changes. | Project maintainer | Remediated | Documentation updated to exactly match remediation evidence. |
| RSK-014 | Invalid CI/action pin | Security | Medium | High | High | Pin full 40-character SHAs and add comment with release tag. | Project maintainer | Remediated | CI action `setup-uv` pinned to full SHA and verified via `git ls-remote`. |
| RSK-015 | Floating build-tool version | Technical | Medium | Medium | Medium | Pin `uv` to explicit version (`0.12.0`) in CI workflow. | Project maintainer | Remediated | CI `ci.yml` updated to use `version: "0.12.0"`. |
| RSK-016 | Verification tests not proving their named invariant | Quality | High | High | High | Write meaningful tests that explicitly mock and assert constraints. | Project maintainer | Remediated | `test_package_metadata.py` rewritten to block sockets and clear env. |
| RSK-017 | Security scanner configured without fail-closed enforcement | Security | High | High | High | Integrate `detect-secrets` into `pre-commit` hook and enforce on all tracked files. | Project maintainer | Remediated | `.pre-commit-config.yaml` updated and tested successfully. |
| RSK-018 | Documentation overstating local verification | Project | High | Medium | High | Explicitly mark phase gates as pending external audit until confirmed. | Project maintainer | Remediated | Phase report and project status updated to reflect accurate state. |
| RSK-019 | Inconsistent Ruff tooling versions and targets | Technical | Low | Low | Low | Align Ruff versions and target configurations across lockfile, `pyproject.toml`, and `.pre-commit-config.yaml`. | Project maintainer | Remediated | Lockfile, project config, and pre-commit all use Ruff `0.16.1` and target `py314`. |
