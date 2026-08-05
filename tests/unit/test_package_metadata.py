import importlib.metadata
import sys
from collections.abc import Generator
from unittest.mock import patch

import pytest


@pytest.fixture(autouse=True)
def clean_import() -> Generator[None]:
    """Ensure sentinelrag is not cached in sys.modules for each test."""
    if "sentinelrag" in sys.modules:
        del sys.modules["sentinelrag"]
    yield


def test_package_version_consistency() -> None:
    """Ensure the package version matches the installed distribution metadata."""
    import sentinelrag  # noqa: F401

    assert hasattr(sentinelrag, "__version__")

    # Compare with installed distribution metadata
    dist_version = importlib.metadata.version("sentinelrag")
    assert sentinelrag.__version__ == dist_version
    assert sentinelrag.__version__ == "0.1.0"


def test_no_network_access_on_import() -> None:
    """Ensure importing the package does not trigger network initialization."""
    # Block socket creation to catch any network activity during import
    err = RuntimeError("Forbidden network access during import")
    with patch("socket.socket", side_effect=err):
        import sentinelrag  # noqa: F401

    assert "sentinelrag" in sys.modules


def test_no_environment_secrets_required(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure import does not crash if environment variables are absent."""
    # Clear typical sentinelrag environment variables to test default safe state
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("PGPASSWORD", raising=False)

    import sentinelrag  # noqa: F401

    assert "sentinelrag" in sys.modules
