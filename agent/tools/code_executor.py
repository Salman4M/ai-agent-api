import subprocess #to seperate user's code and run it in different Python process
import sys
import tempfile # to create temporary files and write user's code in it
import os

BLOCKED_IMPORTS = [
    "os", "sys", "subprocess", "shutil", "pathlib",
    "socket", "requests", "httpx", "urllib", "ftplib",
    "importlib", "builtins", "eval", "exec"
]


def code_executor(code:str) -> str:
    try:
        for blocked in BLOCKED_IMPORTS:
            if f"import {blocked}" in code or f"from {blocked}" in code:
                return f"Error: import '{blocked}' is not allowed"
        
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False
        ) as f:
            f.write(code)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=10
        )

        os.unlink(tmp_path)

        output = result.stdout.strip()
        if result.returncode !=0:
            return f"Error: {result.stderr.strip()}"
        
        return output if output else "Code executed successfully without output"
    
    except subprocess.TimeoutExpired:
        return "Error: code execution time out after 10 seconds"
    except Exception as e:
        return f"Error: {str(e)}"
            
        
