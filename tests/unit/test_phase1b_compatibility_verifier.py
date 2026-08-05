import importlib.metadata
import os
import socket
from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.verify_phase1b_compatibility import (
    NetworkBlockedError,
    VerificationError,
    block_network,
    main,
    parse_requirements,
    scrub_secrets,
    verify_distributions,
)

FAKE_TOML_CONTENT = """
[dependency-groups]
phase1b-compat = [
    "pydantic==2.13.4",
    "pydantic-settings==2.14.2",
    "httpx==0.28.1",
]
"""


@pytest.fixture
def fake_pyproject(tmp_path: Path) -> Path:
    toml_path = tmp_path / "pyproject.toml"
    toml_path.write_text(FAKE_TOML_CONTENT)
    return toml_path


def test_valid_exact_requirement_parsing(fake_pyproject: Path) -> None:
    parsed = parse_requirements(fake_pyproject)
    assert parsed == {
        "pydantic": "2.13.4",
        "pydantic-settings": "2.14.2",
        "httpx": "0.28.1",
    }


def test_rejection_of_non_exact_requirement(tmp_path: Path) -> None:
    toml_path = tmp_path / "pyproject.toml"
    toml_path.write_text("""
[dependency-groups]
phase1b-compat = [
    "pydantic>=2.13.4",
]
""")
    with pytest.raises(VerificationError, match="does not use exact '==' pinning"):
        parse_requirements(toml_path)


def test_rejection_of_extras_and_url_requirements(tmp_path: Path) -> None:
    toml_path = tmp_path / "pyproject.toml"
    toml_path.write_text("""
[dependency-groups]
phase1b-compat = [
    "pydantic[extra]==2.13.4",
]
""")
    with pytest.raises(VerificationError, match="contains invalid syntax"):
        parse_requirements(toml_path)


def test_missing_dependency_group(tmp_path: Path) -> None:
    toml_path = tmp_path / "pyproject.toml"
    toml_path.write_text("[dependency-groups]\nother = []")
    with pytest.raises(VerificationError, match="not found in pyproject.toml"):
        parse_requirements(toml_path)


def test_empty_dependency_group(tmp_path: Path) -> None:
    toml_path = tmp_path / "pyproject.toml"
    toml_path.write_text("[dependency-groups]\nphase1b-compat = []")
    with pytest.raises(VerificationError, match="is empty"):
        parse_requirements(toml_path)


def test_exact_dependency_set_enforcement() -> None:
    expected = {"pydantic": "2.13.4", "httpx": "0.28.1"}
    with pytest.raises(
        VerificationError, match="Dependency group does not exactly match"
    ):
        verify_distributions(expected)


def test_mapping_mismatch_detection() -> None:
    expected = {"pydantic": "2.13.4", "pydantic-settings": "2.14.2", "httpx": "0.28.1"}
    with (
        patch(
            "scripts.verify_phase1b_compatibility.DIST_TO_MODULE",
            {"pydantic": "pydantic"},
        ),
        pytest.raises(
            VerificationError, match="DIST_TO_MODULE mapping keys do not exactly match"
        ),
    ):
        verify_distributions(expected)


def test_installed_version_mismatch_detection(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = {"pydantic": "9.9.9", "pydantic-settings": "2.14.2", "httpx": "0.28.1"}

    def fake_version(name: str) -> str:
        return "1.0.0"

    monkeypatch.setattr(importlib.metadata, "version", fake_version)
    with pytest.raises(VerificationError, match="Version mismatch"):
        verify_distributions(expected)


def test_missing_distribution_detection(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = {"pydantic": "2.13.4", "pydantic-settings": "2.14.2", "httpx": "0.28.1"}

    def fake_version(name: str) -> str:
        raise importlib.metadata.PackageNotFoundError()

    monkeypatch.setattr(importlib.metadata, "version", fake_version)
    with pytest.raises(VerificationError, match="is not installed"):
        verify_distributions(expected)


def test_successful_import_path(monkeypatch: pytest.MonkeyPatch) -> None:
    expected = {"pydantic": "2.13.4", "pydantic-settings": "2.14.2", "httpx": "0.28.1"}

    def fake_version(name: str) -> str:
        return expected[name]

    imported_modules = []

    def fake_import(name: str) -> None:
        imported_modules.append(name)

    monkeypatch.setattr(importlib.metadata, "version", fake_version)
    monkeypatch.setattr("importlib.import_module", fake_import)
    verify_distributions(expected)
    assert "pydantic" in imported_modules


def test_network_connection_blocked_during_verification() -> None:
    with block_network():
        with pytest.raises(NetworkBlockedError):
            socket.socket.connect(None, None)  # type: ignore
        with pytest.raises(NetworkBlockedError):
            socket.create_connection(None)  # type: ignore


def test_network_functions_restored_after_success() -> None:
    orig_connect = socket.socket.connect
    orig_create = socket.create_connection
    with block_network():
        pass
    assert socket.socket.connect is orig_connect
    assert socket.create_connection is orig_create


def test_network_functions_restored_after_failure() -> None:
    orig_connect = socket.socket.connect
    orig_create = socket.create_connection
    try:
        with block_network():
            raise ValueError("Some error")
    except ValueError:
        pass
    assert socket.socket.connect is orig_connect
    assert socket.create_connection is orig_create


def test_secret_variables_absent_during_import() -> None:
    os.environ["OPENAI_API_KEY"] = "supersecret"  # pragma: allowlist secret
    try:
        with scrub_secrets():
            assert "OPENAI_API_KEY" not in os.environ
    finally:
        os.environ.pop("OPENAI_API_KEY", None)


def test_secret_variables_restored_after_success() -> None:
    os.environ["ANTHROPIC_API_KEY"] = "supersecret2"  # pragma: allowlist secret
    try:
        with scrub_secrets():
            pass
        val = os.environ["ANTHROPIC_API_KEY"]
        assert val == "supersecret2"  # pragma: allowlist secret
    finally:
        os.environ.pop("ANTHROPIC_API_KEY", None)


def test_secret_variables_restored_after_failure() -> None:
    os.environ["HF_TOKEN"] = "supersecret3"  # pragma: allowlist secret
    try:
        try:
            with scrub_secrets():
                raise ValueError("error")
        except ValueError:
            pass
        val = os.environ["HF_TOKEN"]
        assert val == "supersecret3"  # pragma: allowlist secret
    finally:
        os.environ.pop("HF_TOKEN", None)


def test_failure_returns_non_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(Path("/"))  # ensure pyproject.toml not found
    result = main()
    assert result == 1


def test_success_returns_zero(
    fake_pyproject: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(fake_pyproject.parent)

    def fake_version(name: str) -> str:
        return {"pydantic": "2.13.4", "pydantic-settings": "2.14.2", "httpx": "0.28.1"}[
            name
        ]

    monkeypatch.setattr(importlib.metadata, "version", fake_version)
    monkeypatch.setattr("importlib.import_module", lambda name: None)

    result = main()
    assert result == 0
