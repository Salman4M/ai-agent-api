import pytest
from agent.tools.calculator import calculator
from agent.tools.code_executor import code_executor
from agent.tools.web_search import web_search


def test_calculator_addition():
    assert calculator("2 + 3") == "5"

def test_calculator_multiplication():
    assert calculator("2340 * 0.15") == "351.0"

def test_calculator_power():
    assert calculator("2 ** 10") == "1024"

def test_calculator_divison():
    assert calculator("10 / 4") == "2.5"

def test_calculator_divison_by_zero():
    assert calculator("10 / 0") == "Error: division by zero"

def test_calculator_blocks_import():
    result = calculator("__import__('os')")
    assert "Error" in result

def test_calculator_blocks_function_call():
    result = calculator("len(hello)")
    assert "Error" in result

def test_calculator_complex_expression():
    assert calculator("(100 + 50) * 2 / 3") == "100.0"

def test_code_executor_simple_print():
    assert code_executor("print(2 + 2)") == "4"

def test_code_executor_loop():
    result = code_executor("for i in range(3): print(i)")
    assert result == "0\n1\n2"

def test_code_executor_blocks_os():
    result = code_executor("import os")
    assert "Error" in result

def test_code_executor_blocks_subprocess():
    result = code_executor("import subprocess")
    assert "Error" in result

def test_code_executor_timout():
    result = code_executor("while True: pass")
    assert "time out" in result.lower()


def test_code_executor_syntax_error():
    result = code_executor("def broken(")
    assert "Error" in result


def test_web_search_returns_results():
    result = web_search("python programming language")
    assert len(result) > 0
    assert "Title:" in result

def test_web_search_no_results_handling():
    result = web_search("alflefl23532ealgsl2342532fsds")
    assert isinstance(result,str)