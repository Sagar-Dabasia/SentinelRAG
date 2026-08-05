import socket
from collections.abc import Iterator
from pathlib import Path

import pytest

from scripts.verify_phase1b_compatibility import (
    block_network,
    get_expected_versions,
    main,
)


@pytest.fixture
def unblock_network() -> Iterator[None]:
    original_connect = socket.socket.connect
    original_create = socket.create_connection
    yield
    socket.socket.connect = original_connect  # type: ignore[method-assign]
    socket.create_connection = original_create


def test_network_blocker(unblock_network: None) -> None:
    block_network()
    with pytest.raises(RuntimeError, match="Network connection blocked"):
        socket.socket.connect(socket.socket(), ("8.8.8.8", 80))
    with pytest.raises(RuntimeError, match="Network connection blocked"):
        socket.create_connection(("8.8.8.8", 80))


def test_requirement_parsing_valid(monkeypatch: pytest.MonkeyPatch) -> None:
    valid_toml = (
        "phase1b-compat = [\n"
        '    "pydantic==2.13.4",\n'
        '    "pydantic-settings==2.14.2",\n'
        '    "httpx==0.28.1",\n'
        "]\n"
    )
    monkeypatch.setattr(Path, "read_text", lambda *args, **kwargs: valid_toml)
    monkeypatch.setattr(Path, "exists", lambda *args, **kwargs: True)

    versions = get_expected_versions()
    assert versions == {
        "pydantic": "2.13.4",
        "pydantic-settings": "2.14.2",
        "httpx": "0.28.1",
    }


def test_rejection_of_non_exact_requirements(monkeypatch: pytest.MonkeyPatch) -> None:
    invalid_toml = 'phase1b-compat = [\n    "pydantic>=2.13.4",\n]\n'
    monkeypatch.setattr(Path, "read_text", lambda *args, **kwargs: invalid_toml)
    monkeypatch.setattr(Path, "exists", lambda *args, **kwargs: True)

    with pytest.raises(RuntimeError, match="Non-exact requirement found:"):
        get_expected_versions()


def test_missing_distribution_detection(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    # Set a fake requirement for a package that isn't installed
    fake_toml = (
        "phase1b-compat = [\n"
        '    "pydantic==2.13.4",\n'
        '    "pydantic-settings==2.14.2",\n'
        '    "httpx==0.28.1",\n'
        '    "fake-pkg==1.0.0",\n'
        "]\n"
    )
    monkeypatch.setattr(Path, "read_text", lambda *args, **kwargs: fake_toml)
    monkeypatch.setattr(Path, "exists", lambda *args, **kwargs: True)

    import scripts.verify_phase1b_compatibility as verifier

    monkeypatch.setattr(verifier, "DIST_TO_MODULE", {"fake-pkg": "fake_pkg"})

    result = main()
    assert result == 1
    captured = capsys.readouterr()
    assert "fake-pkg: Not installed." in captured.out


def test_version_mismatch_detection(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake_toml = (
        "phase1b-compat = [\n"
        '    "pydantic==99.99.99",\n'
        '    "pydantic-settings==2.14.2",\n'
        '    "httpx==0.28.1",\n'
        "]\n"
    )
    monkeypatch.setattr(Path, "read_text", lambda *args, **kwargs: fake_toml)
    monkeypatch.setattr(Path, "exists", lambda *args, **kwargs: True)

    result = main()
    assert result == 1
    captured = capsys.readouterr()
    assert "pydantic: Version mismatch" in captured.out


def test_successful_import_path_and_mapping(
    unblock_network: None,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # We don't mock the pyproject.toml here, so it reads the actual one.
    # We assume the environment has the correct packages installed.
    # If the tests run in an environment where phase1b-compat is installed correctly,
    # main() should return 0.
    # To avoid failures if the env isn't perfect, we can't assume much.
    # The prompt says: "Require installation, imports and all existing tests to pass."
    # Since we must verify successful import path and it's a test for script logic,
    # we can run main() and see if it passes. If it doesn't, the test fails,
    # which is correct if the environment isn't set up. But the test environment
    # WILL have the packages installed.

    result = main()
    captured = capsys.readouterr()
    # If the real env has wrong versions, main() returns 1 and the test would fail.
    # That is desired: tests only pass when the env matches pyproject.toml exactly.
    assert result == 0
    assert "pydantic (v" in captured.out
    assert "pydantic-settings (v" in captured.out
    assert "httpx (v" in captured.out
    assert "Status: PASSED" in captured.out
