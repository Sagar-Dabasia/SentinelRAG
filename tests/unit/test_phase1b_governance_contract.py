import re
from pathlib import Path


def test_no_fix_scripts() -> None:
    root = Path(__file__).parent.parent.parent
    fix_scripts = list(root.glob("fix*.py"))
    assert not fix_scripts, f"Found temporary repair scripts: {fix_scripts}"


def test_env_example_safe_defaults() -> None:
    env_path = Path(__file__).parent.parent.parent / ".env.example"
    content = env_path.read_text(encoding="utf-8")

    assert "SENTINELRAG_PROVIDER=disabled" in content

    # Assert no active uncommented endpoint or model
    assert not re.search(r"^\s*SENTINELRAG_ENDPOINT=", content, re.MULTILINE)
    assert not re.search(r"^\s*SENTINELRAG_MODEL_IDENTIFIER=", content, re.MULTILINE)


def test_readme_progress() -> None:
    readme_path = Path(__file__).parent.parent.parent / "README.md"
    content = readme_path.read_text(encoding="utf-8")

    assert "Verified project progress: 8%." in content
    assert (
        "Phase 1B is implemented but failed audit and is under remediation." in content
    )
    assert "Phase 1C is not approved." in content


def test_project_status_progress() -> None:
    status_path = Path(__file__).parent.parent.parent / "docs" / "PROJECT_STATUS.md"
    content = status_path.read_text(encoding="utf-8")

    assert "Verified project progress: 8%" in content
    assert (
        "Last independently audited commit: 412157a77c01be761597d1d672cc1610fc4028c3"
        in content
    )
    assert "Last audit verdict: FAIL" in content
    assert "Phase 1B gate: REMEDIATION IN PROGRESS" in content
    assert "Phase 1C: NOT APPROVED" in content


def test_risk_register_not_remediated() -> None:
    risk_path = Path(__file__).parent.parent.parent / "docs" / "RISK_REGISTER.md"
    content = risk_path.read_text(encoding="utf-8")

    # Assert RSK-027 and RSK-028 are not marked as Remediated.
    rsk_27 = re.search(r"\|\s*RSK-027\s*\|.*?\|\s*Remediated\s*\|", content)
    assert not rsk_27, "RSK-027 should not be marked Remediated before audit."

    rsk_28 = re.search(r"\|\s*RSK-028\s*\|.*?\|\s*Remediated\s*\|", content)
    assert not rsk_28, "RSK-028 should not be marked Remediated before audit."


def test_phase1b_report_not_completed() -> None:
    report_path = (
        Path(__file__).parent.parent.parent
        / "docs"
        / "phases"
        / "PHASE_01B_MODEL_PROVIDER_CONTRACTS.md"
    )
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8")
        assert "**Completed**" not in content
        assert "Candidate commit: `PENDING`" in content
        assert "Push: `PENDING`" in content
        assert "External audit: `PENDING`" in content


def test_adrs_not_accepted() -> None:
    decisions_dir = Path(__file__).parent.parent.parent / "docs" / "decisions"
    adrs = [
        "ADR-0008-Local-Model-Protocol.md",
        "ADR-0009-Strict-Loopback-Only-Access.md",
        "ADR-0010-MockTransport-Testing.md",
    ]

    for adr in adrs:
        adr_path = decisions_dir / adr
        if adr_path.exists():
            content = adr_path.read_text(encoding="utf-8")
            assert "Status: Accepted" not in content
            assert "Proposed" in content
            assert "pending independent Phase 1B audit" in content


def test_phase1a_closure_text_exists() -> None:
    report_path = (
        Path(__file__).parent.parent.parent
        / "docs"
        / "phases"
        / "PHASE_01_COMPATIBILITY_REVIEW.md"
    )
    content = report_path.read_text(encoding="utf-8")
    sha = "8e93ae2d9fa00681360d36b215b25bc549c5700c"  # pragma: allowlist secret
    assert sha in content
    assert "PASS WITH WARNINGS" in content


def test_no_ci_passed_claim() -> None:
    report_path = (
        Path(__file__).parent.parent.parent
        / "docs"
        / "phases"
        / "PHASE_01B_MODEL_PROVIDER_CONTRACTS.md"
    )
    if report_path.exists():
        content = report_path.read_text(encoding="utf-8")
        assert "CI passed" not in content.lower()
