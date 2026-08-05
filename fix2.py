import os
import re

files = [
    "tests/unit/models/test_disabled.py",
    "tests/unit/models/test_http.py",
    "tests/unit/models/test_ollama.py",
    "tests/unit/models/test_lm_studio.py"
]

for filepath in files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # We will replace all occurrences of @pytest.mark.asyncio
    content = content.replace("@pytest.mark.asyncio\n", "")
    
    # We will replace `async def test_` with `def _async_test_`
    # and then append a non-async wrapper at the end.
    # No, that's complex. Let's just use regular expressions carefully.
    
    # Or just use pytest-asyncio and ignore the prompt? No, I must obey the prompt: "Do not add an async pytest plugin. Use standard-library async execution where necessary."
    
    new_content = ""
    in_func = False
    
    for line in content.split("\n"):
        if line.startswith("async def test_"):
            new_content += line.replace("async def ", "def ") + "\n"
            new_content += "    import asyncio\n"
            new_content += "    async def _run():\n"
            in_func = True
        elif in_func and line and not line.startswith(" ") and not line.startswith("\t") and not line.startswith(")"):
            # End of function
            new_content += "    asyncio.run(_run())\n"
            in_func = False
            new_content += line + "\n"
        elif in_func:
            if line.startswith(") -> None:"):
                new_content += line + "\n"
            else:
                if line == "":
                    new_content += "\n"
                else:
                    new_content += "    " + line + "\n"
        else:
            new_content += line + "\n"

    if in_func:
        new_content += "    asyncio.run(_run())\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)
