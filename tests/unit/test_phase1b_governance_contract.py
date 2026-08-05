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


def test_ci_hard_gates() -> None:
    ci_path = Path(__file__).parent.parent.parent / ".github" / "workflows" / "ci.yml"
    content = ci_path.read_text(encoding="utf-8")

    assert "tests/unit/test_phase1b_governance_contract.py" in content
    assert "--cov-branch" in content
    assert "--cov-fail-under=95" in content


def test_http_mocktransport_not_patched() -> None:
    test_http_path = Path(__file__).parent / "models" / "test_http.py"
    content = test_http_path.read_text(encoding="utf-8")

    assert "httpx.MockTransport" in content
    assert "patch.object" not in content


def test_project_status_contract() -> None:
    status_path = Path(__file__).parent.parent.parent / "docs" / "PROJECT_STATUS.md"
    content = status_path.read_text(encoding="utf-8")

    assert "Verified project progress: 8%" in content
    assert "Phase 1C: NOT APPROVED" in content
    assert (
        "Last independently audited commit: 63f40577157b02a610f725a6791661b1e4a773e3"
        in content
    )
    assert "Last audit verdict: FAIL" in content


def test_phase1b_report_contract() -> None:
    report_path = (
        Path(__file__).parent.parent.parent
        / "docs"
        / "phases"
        / "PHASE_01B_MODEL_PROVIDER_CONTRACTS.md"
    )
    content = report_path.read_text(encoding="utf-8")

    assert "#22" in content
    assert "#23" in content
    assert (
        "| Requirement | Evidence file/test | Verification command | Exact result |"
        in content
    )

    # Assert report does not claim loopback eliminates risk
    assert (
        "eliminat" not in content.lower()
        or "loopback" not in content.lower()
        or ("does not protect against compromised local services" in content.lower())
    )

    # Assert report does not claim offline tests guarantee no leaks
    assert (
        "guarantee no leaks" not in content.lower()
        or "does not guarantee that all present or future application "
        "paths can never leak data"
        in content.lower()
    )


def test_adr0009_contract() -> None:
    adr_path = (
        Path(__file__).parent.parent.parent
        / "docs"
        / "decisions"
        / "ADR-0009-Strict-Loopback-Only-Access.md"
    )
    content = adr_path.read_text(encoding="utf-8")

    assert "127.0.0.0/8" in content
    assert "::1" in content
    assert "localhost" in content


def test_adr0006_contract() -> None:
    adr_path = (
        Path(__file__).parent.parent.parent
        / "docs"
        / "decisions"
        / "ADR-0006-local-model-and-embedding-stack.md"
    )
    content = adr_path.read_text(encoding="utf-8")

    assert "Status: Accepted" not in content


def test_risk_register_wording() -> None:
    risk_path = Path(__file__).parent.parent.parent / "docs" / "RISK_REGISTER.md"
    content = risk_path.read_text(encoding="utf-8")

    # Assert RSK-027 and RSK-028 use risk-reduction wording
    assert "prevent" not in content.lower() or (
        "reduce" in content.lower() and "eliminate" not in content.lower()
    )
