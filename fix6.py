import os
import re

# Fix test_settings.py
filepath = "tests/unit/config/test_settings.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_content = re.sub(r'(endpoint=".*?"),', r'\1,  # type: ignore[arg-type]', content)
# For the one without a trailing comma:
new_content = re.sub(r'(endpoint=".*?")\n', r'\1  # type: ignore[arg-type]\n', new_content)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)

# Fix test_lm_studio.py Any import and content typing
filepath = "tests/unit/models/test_lm_studio.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("import asyncio", "import asyncio\nfrom typing import Any")
# Fix MockTransport
content = content.replace("return self.response_factory(request)", "return self.response_factory(request)  # type: ignore")
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

# Fix test_ollama.py
filepath = "tests/unit/models/test_ollama.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("return self.response_factory(request)", "return self.response_factory(request)  # type: ignore")
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

# Fix lm_studio.py typing
filepath = "src/sentinelrag/models/lm_studio.py"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('model_ident: str = data.get("model", self._settings.model_identifier)', 'model_ident = str(data.get("model", self._settings.model_identifier))')
with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)
