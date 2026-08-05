import re
from pathlib import Path


def test_python_contract() -> None:
    pyproject = Path("pyproject.toml").read_text()
    assert 'requires-python = ">=3.14,<3.15"' in pyproject
    assert 'target-version = "py314"' in pyproject
    assert 'python_version = "3.14"' in pyproject


def test_project_status_contract() -> None:
    status = Path("docs/PROJECT_STATUS.md").read_text()
    assert "Current activity: Phase 1B remediation pending external audit" in status
    assert "Phase 1 implementation status: IN PROGRESS" in status
    assert (
        "Last independently audited commit: 412157a77c01be761597d1d672cc1610fc4028c3"
        in status
    )
    assert "Last audit verdict: FAIL" in status
    assert "Phase 1A gate: PASSED WITH WARNINGS" in status
    assert "Verified project progress: 8%" in status
    assert "Phase 1B gate: REMEDIATION IN PROGRESS" in status
    assert (
        "Next action: independent remote audit of the Phase 1B remediation "
        "commit" in status
    )

    open_risks_line = [
        line for line in status.splitlines() if line.startswith("Open risks:")
    ][0]
    assert "RSK-026" in open_risks_line


def test_risk_register_contract() -> None:
    register = Path("docs/RISK_REGISTER.md").read_text()

    rsk022 = re.search(
        r"\|\s*RSK-022\s*\|.*?\|\s*High\s*\|\s*High\s*\|\s*High\s*\|", register
    )
    assert rsk022 is not None, "RSK-022 does not have High, High, High"

    assert (
        " trust_remote_code=False" in register
        or "Enforce trust_remote_code=False" in register
    )
    assert " rust_remote_code" not in register
    assert "\trust_remote_code" not in register

    assert "RSK-026" in register
    rsk026_line = [line for line in register.splitlines() if "RSK-026" in line][0]
    assert "Monitoring" in rsk026_line or "Pending audit" in rsk026_line
    assert "Remediated" not in rsk026_line
    assert "remote CI" not in rsk026_line
    assert "external audit passed" not in rsk026_line.lower()

    assert "RSK-026" in register, "Open-risk references must include RSK-026"


def test_adr0007_contract() -> None:
    adr = Path("docs/decisions/ADR-0007-phase-1-scope-aware-data-model.md").read_text()
    assert "UUIDv4" in adr
    assert "created_at" in adr
    assert "identity does not create isolation" in adr.lower()
    assert "only needs to swap" not in adr.lower()
    t1_p1 = "authorization, scoped relational/vector queries, "
    t1_p2 = "citation authorization, revocation/deletion and cross-user negative tests"
    t1 = t1_p1 + t1_p2

    t2_p1 = (
        "authorization, scoped relational and vector queries, citation authorization, "
    )
    t2_p2_a = "deletion and revocation enforcement, guessed-identifier tests "
    t2_p2_b = "and cross-user canary tests"
    t2_p2 = t2_p2_a + t2_p2_b
    t2 = t2_p1 + t2_p2

    assert t1 in adr.lower() or t2 in adr.lower()


def test_compatibility_report_contract() -> None:
    report = Path("docs/phases/PHASE_01_COMPATIBILITY_REVIEW.md").read_text()

    expected_headings = [
        "Failed broad-stack experiment",
        "Failed remediation commit",
        "Staged compatibility decision",
        "Current Phase 1B exact dependency matrix",
        "Python 3.14 evidence",
        "Local verification evidence",
        "Deferred Phase 1C decisions",
        "Deferred Phase 1D decisions",
        "Deferred Phase 1F decisions",
        "Requirements-to-evidence matrix",
        "Limitations",
        "Phase 1A closure complete",
    ]
    for h in expected_headings:
        assert h in report, f"Missing heading: {h}"

    false_claims = [
        "trust_remote_code=False is enforced in initialization contracts",
        "Full Phase 1 stack approved",
        "Phase 1B approved",
        "External audit passed",
        "GitHub CI passed",
    ]
    for claim in false_claims:
        assert claim not in report, f"Contains false claim: {claim}"


def test_no_false_claims_in_documents() -> None:
    for doc_path in [
        "docs/PROJECT_STATUS.md",
        "docs/phases/PHASE_01_COMPATIBILITY_REVIEW.md",
    ]:
        text = Path(doc_path).read_text().lower()
        assert "phase 1b is approved" not in text
        assert "phase 1b approved" not in text
        assert "github ci passed" not in text
