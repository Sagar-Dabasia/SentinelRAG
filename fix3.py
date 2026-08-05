import os
import re

files = [
    "tests/unit/config/test_settings.py",
    "tests/unit/models/test_factory.py"
]

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    new_content = re.sub(r'endpoint="(.*?)"(?!.*type: ignore)', r'endpoint="\1",  # type: ignore[arg-type]', content)
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
