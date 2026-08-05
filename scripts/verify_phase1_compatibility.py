import sys
import platform
import importlib

print(f"Python version: {sys.version}")
print(f"Platform: {platform.platform()}")

expected_versions = {
    "fastapi": "0.111.0",
    "pydantic": "2.8.0",
    "pydantic_settings": "2.3.0",
    "uvicorn": "0.30.0",
    "httpx": "0.27.0",
    "python_multipart": "0.0.9",
    "psycopg": "3.3.4",
    "sqlalchemy": "2.0.30",
    "alembic": "1.13.0",
    "pgvector": "0.5.0",
    "streamlit": "1.36.0",
    "pypdf": "4.2.0",
    "sentence_transformers": "3.0.0",
    "torch": "2.9.1",
    "transformers": "4.44.0"
}

try:
    from importlib.metadata import version
except ImportError:
    import pkg_resources
    def version(pkg):
        return pkg_resources.get_distribution(pkg).version

# Test pgvector vector construction without connecting
from pgvector.sqlalchemy import Vector
try:
    v = Vector(384)
    print("pgvector SQLAlchemy Vector(384) constructed successfully.")
except Exception as e:
    print(f"Error constructing Vector: {e}")
    sys.exit(1)

# Import everything required without network/database
for pkg, expected in expected_versions.items():
    try:
        mod_name = "multipart" if pkg == "python_multipart" else pkg
        mod = importlib.import_module(mod_name)
        actual = version(pkg.replace("_", "-"))
        if actual != expected:
            print(f"Version mismatch for {pkg}: expected {expected}, got {actual}")
            sys.exit(1)
        print(f"Successfully imported {pkg} (version {actual})")
    except Exception as e:
        print(f"Failed to import {pkg}: {e}")
        sys.exit(1)

print("All dependencies imported successfully.")
sys.exit(0)
