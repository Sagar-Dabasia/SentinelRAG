import importlib.metadata
import os
import platform
import socket
import sys
import tomllib
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

EXPECTED_DISTRIBUTIONS = {"pydantic", "pydantic-settings", "httpx"}
DIST_TO_MODULE = {
    "pydantic": "pydantic",
    "pydantic-settings": "pydantic_settings",
    "httpx": "httpx",
}

SECRETS_TO_SCRUB = [
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "AZURE_OPENAI_API_KEY",
    "HUGGINGFACE_TOKEN",
    "HF_TOKEN",
    "OLLAMA_HOST",
    "LM_STUDIO_API_KEY",
    "SENTINELRAG_SECRET_KEY",
    "SENTINELRAG_DATABASE_URL",
]


class VerificationError(Exception):
    """Base exception for verification failures."""


class NetworkBlockedError(Exception):
    """Exception raised when a network call is blocked."""


@contextmanager
def block_network() -> Generator[None]:
    original_connect = socket.socket.connect
    original_create = socket.create_connection

    def blocked_connect(self: Any, address: Any) -> None:
        raise NetworkBlockedError(
            "Network connections are blocked during verification."
        )

    def blocked_create(
        address: Any,
        timeout: Any = None,
        source_address: Any = None,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        raise NetworkBlockedError(
            "Network connections are blocked during verification."
        )

    socket.socket.connect = blocked_connect  # type: ignore[method-assign]
    socket.create_connection = blocked_create

    print("Network blocker installed.")
    try:
        yield
    finally:
        socket.socket.connect = original_connect  # type: ignore[method-assign]
        socket.create_connection = original_create
        print("Network blocker restored.")


@contextmanager
def scrub_secrets() -> Generator[None]:
    saved_secrets = {}
    for secret in SECRETS_TO_SCRUB:
        if secret in os.environ:
            saved_secrets[secret] = os.environ.pop(secret)

    print("Secret environment scrubbed.")
    try:
        yield
    finally:
        for secret, value in saved_secrets.items():
            os.environ[secret] = value
        print("Secret environment restored.")


def parse_requirements(pyproject_path: Path) -> dict[str, str]:
    if not pyproject_path.exists():
        raise VerificationError("pyproject.toml not found.")

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    try:
        deps = data["dependency-groups"]["phase1b-compat"]
    except KeyError:
        raise VerificationError(
            "Dependency group 'phase1b-compat' not found in pyproject.toml."
        ) from None

    if not deps:
        raise VerificationError("Dependency group 'phase1b-compat' is empty.")

    parsed = {}
    for req in deps:
        if "==" not in req:
            raise VerificationError(
                f"Requirement '{req}' does not use exact '==' pinning."
            )
        if (
            ">=" in req
            or "~=" in req
            or "*" in req
            or ";" in req
            or "[" in req
            or "@" in req
        ):
            msg = (
                f"Requirement '{req}' contains invalid syntax "
                "(markers, extras, wildcards)."
            )
            raise VerificationError(msg)

        parts = req.split("==")
        if len(parts) != 2:
            raise VerificationError(f"Requirement '{req}' is malformed.")

        name = parts[0].strip()
        version = parts[1].strip()

        if not name or not version:
            raise VerificationError(f"Requirement '{req}' is malformed.")

        parsed[name] = version

    return parsed


def verify_distributions(expected: dict[str, str]) -> None:
    expected_keys = set(expected.keys())
    if expected_keys != EXPECTED_DISTRIBUTIONS:
        raise VerificationError(
            "Dependency group does not exactly match the allowed Phase 1B set."
        )

    mapping_keys = set(DIST_TO_MODULE.keys())
    if mapping_keys != EXPECTED_DISTRIBUTIONS:
        raise VerificationError(
            "DIST_TO_MODULE mapping keys do not exactly match the allowed Phase 1B set."
        )

    for dist, expected_version in expected.items():
        try:
            installed_version = importlib.metadata.version(dist)
            print(f"Exact installed version for {dist}: {installed_version}")
            if installed_version != expected_version:
                msg = (
                    f"Version mismatch for {dist}. Expected {expected_version}, "
                    f"got {installed_version}"
                )
                raise VerificationError(msg)
        except importlib.metadata.PackageNotFoundError:
            raise VerificationError(f"{dist} is not installed.") from None

        module_name = DIST_TO_MODULE[dist]
        try:
            with block_network(), scrub_secrets():
                importlib.import_module(module_name)
        except Exception as e:
            raise VerificationError(
                f"Failed to import {module_name} for {dist}: {type(e).__name__}"
            ) from e


def main() -> int:
    print(f"Python version: {sys.version}")
    print(f"Platform: {platform.platform()}")

    try:
        pyproject_path = Path("pyproject.toml")
        expected = parse_requirements(pyproject_path)
        print(f"Exact expected versions: {expected}")
        verify_distributions(expected)
        print("Final PASSED")
        return 0
    except VerificationError as e:
        print(f"[FAIL] Verification: {e}")
        print("Final FAILED")
        return 1
    except Exception as e:
        print(f"[FAIL] Unexpected: {type(e).__name__}")
        print("Final FAILED")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
