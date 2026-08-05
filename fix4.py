import os

filepath = "tests/unit/config/test_settings.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# I will just revert it and do it properly.
content = content.replace(',  # type: ignore[arg-type])', ')')
content = content.replace(',  # type: ignore[arg-type]', '')

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
