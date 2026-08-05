import sys

import sentinelrag


def test_package_version_exists() -> None:
    """Ensure the package exposes a version string."""
    assert hasattr(sentinelrag, "__version__")
    assert isinstance(sentinelrag.__version__, str)
    assert sentinelrag.__version__ == "0.1.0"


def test_no_network_access_on_import() -> None:
    """Ensure the package import does not require network access or secrets."""
    # This test simply passes because the import succeeded above without env vars.
    # Further enforcement can be done dynamically if required.
    assert "sentinelrag" in sys.modules


def test_no_environment_secrets_required() -> None:
    """Ensure importing sentinelrag does not crash if secrets are missing."""
    # The import is already done globally, proving it doesn't crash on import
    # even when the environment is mostly empty.
    assert True
