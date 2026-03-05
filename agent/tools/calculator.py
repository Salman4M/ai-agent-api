import ast # for parsing python code and constructing into a AST tree
import operator # for math operations

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
        if op is None:
            raise ValueError(f"Operator not allowed")
        return op(_evaluate(node.left), _evaluate(node.right))
    
    elif isinstance(node,ast.UnaryOp):
        op = ALLOWED_OPERATORS.get(type(node.op))
        if op is None:
            raise ValueError(f"Operator not allowed")
        return op(_evaluate(node.operand))
    else:
        raise ValueError(f"Expression not allowed: {type(node)}")
    
def calculator(expression: str) -> str:
    try:
        tree = ast.parse(expression, mode="eval") # eval means except a single expression, not statements
        result = _evaluate(tree.body)#walk the tree and evaluate it safely. `tree.body` is the root node of the parsed expression.
        return str(result)
    except ZeroDivisionError:    
        return "Error: division by zero"
    except Exception as e:
        return f"Error: {str(e)}"
            

