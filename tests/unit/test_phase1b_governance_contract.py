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


def test_no_artificial_mutations_in_tests() -> None:
    test_models_path = Path(__file__).parent / "models"
    test_config_path = Path(__file__).parent / "config"
    for path in [test_models_path, test_config_path]:
        for file in path.glob("test_*.py"):
            content = file.read_text(encoding="utf-8")
            assert "settings.endpoint = MockUrl()" not in content
            assert 'settings.provider = "unknown"' not in content
            assert "unreachable fallback" not in content.lower()


def test_project_status_contract() -> None:
    status_path = Path(__file__).parent.parent.parent / "docs" / "PROJECT_STATUS.md"
    content = status_path.read_text(encoding="utf-8")

    assert "Verified project progress: 8%" in content
    assert "Phase 1C: NOT APPROVED" in content
    assert (
        "Last independently audited commit: e86581b51e2f1f923df44ce25ff5fbd1a09ac1fd"
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

    assert "#24" in content
    assert (
        "| Requirement | Evidence file/test | Verification command | Exact result |"
        in content
    )
    # Check that current active evidence matrix does not have Exit code 1
    # We'll isolate the current evidence matrix section.
    # It ends before "## Mandatory verification" or EOF.
    active_matrix_start = content.rfind("| Requirement | Evidence file/test |")
    if active_matrix_start != -1:
        active_matrix_section = content[active_matrix_start:]
        assert "Exit code 1" not in active_matrix_section
        assert re.search(r"9[5-9]%|100%", active_matrix_section) is not None, (
            "must record focused coverage >= 95%"
        )
        assert re.search(r"[8-9][0-9]%|100%", active_matrix_section) is not None, (
            "must record repo coverage >= 80%"
        )

    # pragma: allowlist secret
    hash_val = "e86581b51e2f1f923df44ce25ff5fbd1a09ac1fd"  # pragma: allowlist secret
    assert hash_val in content
    assert "External audit: PENDING" in content
    assert "external audit passed" not in content.lower()
    assert "Main test job success" in content
    assert "Phase 1B contracts job success" in content

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
