import importlib
import importlib.metadata
import re
import socket
from pathlib import Path


def block_network() -> None:
    """Intercept and block network calls before importing."""

    def blocked_connect(*args: object, **kwargs: object) -> None:
        raise RuntimeError(
            f"Network connection blocked during verification: {args} {kwargs}"
        )

    # Override the connect methods
    socket.socket.connect = blocked_connect  # type: ignore[method-assign]
    socket.create_connection = blocked_connect  # type: ignore[assignment]


def get_expected_versions() -> dict[str, str]:
    """Parse phase1b-compat dependencies from pyproject.toml."""
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        raise RuntimeError("pyproject.toml not found")

    content = pyproject_path.read_text(encoding="utf-8")
    match = re.search(r"phase1b-compat\s*=\s*\[(.*?)\]", content, re.DOTALL)
    if not match:
        raise RuntimeError("phase1b-compat group not found in pyproject.toml")

    deps_str = match.group(1)
    versions: dict[str, str] = {}
    for line in deps_str.splitlines():
        line = line.strip().strip("\",'")
        if not line:
            continue
        if "==" not in line:
            raise RuntimeError(f"Non-exact requirement found: {line}")
        pkg, ver = line.split("==")
        versions[pkg.strip()] = ver.strip()

    if not versions:
        raise RuntimeError("No dependencies found in phase1b-compat")

    return versions


DIST_TO_MODULE = {
    "pydantic": "pydantic",
    "pydantic-settings": "pydantic_settings",
    "httpx": "httpx",
}


def main() -> int:
    try:
        block_network()
    except Exception as e:
        print(f"Failed to block network: {e}")
        return 1

    try:
        expected_versions = get_expected_versions()
    except Exception as e:
        print(f"Error parsing expected versions: {e}")
        return 1

    print("Phase 1B Compatibility Verification:")
    print("-" * 40)
    has_error = False

    for dist, module in DIST_TO_MODULE.items():
        if dist not in expected_versions:
            print(f"[FAIL] Missing expected configuration for {dist} in pyproject.toml")
            has_error = True
            continue

        expected_ver = expected_versions[dist]

        try:
            # Check version
            actual_ver = importlib.metadata.version(dist)
            if actual_ver != expected_ver:
                print(
                    f"[FAIL] {dist}: Version mismatch "
                    f"(Expected: {expected_ver}, Actual: {actual_ver})"
                )
                has_error = True
                continue

            # Check import (proves no network/secret requirements at import time)
            importlib.import_module(module)
            print(
                f"[PASS] {dist} (v{actual_ver}) imported successfully "
                "without network access."
            )

        except importlib.metadata.PackageNotFoundError:
            print(f"[FAIL] {dist}: Not installed.")
            has_error = True
        except RuntimeError as e:
            if "Network connection blocked" in str(e):
                print(f"[FAIL] {dist}: Attempted network access during import.")
            else:
                print(f"[FAIL] {dist}: RuntimeError: {e}")
            has_error = True
        except Exception as e:
            print(f"[FAIL] {dist}: Import error: {e}")
            has_error = True

    if has_error:
        print("-" * 40)
        print("Status: FAILED")
        return 1

    print("-" * 40)
    print("Status: PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
