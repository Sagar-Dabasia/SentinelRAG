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
        
    if "@pytest.mark.asyncio" not in content:
        continue
        
    if "import asyncio" not in content:
        content = "import asyncio\n" + content
        
    # Replace the decorator and async def with a sync def that calls asyncio.run
    # Since indentation is tricky, we'll replace:
    # @pytest.mark.asyncio\nasync def test_something(args):\n
    # with:
    # def test_something(args):\n    async def _run():\n
    # and then we need to indent the rest of the function by 4 spaces.
    # Actually, the easiest way is to use ast or just regex carefully.
    
    lines = content.split('\n')
    new_lines = []
    in_async_test = False
    test_args = ""
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("@pytest.mark.asyncio"):
            i += 1
            def_line = lines[i]
            match = re.match(r"async def (test_\w+)\((.*?)\)(.*?):", def_line)
            if match:
                func_name = match.group(1)
                args = match.group(2)
                ret_type = match.group(3)
                new_lines.append(f"def {func_name}({args}){ret_type}:")
                new_lines.append("    async def _run():")
                
                # Now indent everything until the next def or unindented line
                i += 1
                while i < len(lines) and (lines[i].startswith(" ") or lines[i] == ""):
                    if lines[i] == "":
                        new_lines.append("")
                    else:
                        new_lines.append("    " + lines[i])
                    i += 1
                
                # Add the asyncio.run call
                new_lines.append(f"    asyncio.run(_run())")
                new_lines.append("")
                continue
        new_lines.append(line)
        i += 1
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))
        
