from ddgs import DDGS
import ast
import operator
import subprocess
import sys
import tempfile
import os


BLOCKED_IMPORTS = [
    "os", "sys", "subprocess", "shutil", "pathlib",
    "socket", "requests", "httpx", "urllib", "ftplib",
    "importlib", "builtins", "eval", "exec"
]

ALLOWED_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}

def _evaluate(node):
    if isinstance(node,ast.Constant):
        return node.value
    elif isinstance(node,ast.BinOp):
        op = ALLOWED_OPERATORS.get(type(node.op))
        if not op:
            raise ValueError(f"Operator not allowed")
        return op(_evaluate(node.left), _evaluate(node.right))
    elif isinstance(node,ast.UnaryOp):
        op = ALLOWED_OPERATORS.get(type(node.op))
        if not op:
            raise ValueError(f"Operator not allowed")
        return op(_evaluate(node.operand))
    else:
        raise ValueError(f"Expression not allowed: {type(node).__name__}")


def web_search(query:str)-> str:
    """Search the web for current information using DuckDuckGo.

    Args:
        query: The search query string
    
    Returns:
        Search results as formatted text with titles, URLs and sumamries
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        if not results:
            return "No results found"
        formatted = []
        for r in results:
            formatted.append(f"Title: {r['title']}\nURL: {r['href']}\nSummary: {r['body']}")
        return "\n\n---\n\n".join(formatted)
    except Exception as e:
        return f"Search error: {str(e)}"
    

def calculator(expression: str)->str:
    """Evaluate a mathematical expression safely.

    Args:
        expression: A mathematical expression like '2 + 2' or '10 * 5'

    Returns:
        The result of the calculation as a string
    """
    try:
        tree = ast.parse(expression, mode = 'eval')
        result = _evaluate(tree.body)
        return str(result)
    except ZeroDivisionError:
        return "Error: division by zero"
    except Exception as e:
        return f"Error: {str(e)}"
    

def code_executor(code:str)->str:
    """Execute Python code safely in an isolated subprocess.

    Args:
        code: Python code to execute

    Returns:
        Output of the code execution of error message 
    """
    for blocked in BLOCKED_IMPORTS:
        if f"import {blocked}" in code or f"from {blocked}" in code:
            return f"Error:import {blocked} is not allowed"
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",suffix=".py",delete=False
        )as f:
            f.write(code)
            tmp_path = f.name
        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=10
        )
        os.unlink(tmp_path)
        if result.returncode !=0:
            return f"Error: {result.stderr.strip()}"
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return "Error: code execution time out after 10 seconds"
    except Exception as e:
        return f"Error:{str(e)}"
