import ast

from graphviz import Digraph # to see visualation of AST Tree




def visualize_ast(expression: str):
    tree = ast.parse(expression, mode="eval")
    # Create a Graphviz Digraph object
    dot = Digraph(comment='Python AST')

    def add_node(node, parent_id=None):
        node_id = str(id(node))
        
        # label — what type of node + its value if constant
        if isinstance(node, ast.Constant):
            label = f"Constant\n{node.value}"
        elif isinstance(node, ast.BinOp):
            label = f"BinOp\n{type(node.op).__name__}"
        elif isinstance(node, ast.UnaryOp):
            label = f"UnaryOp\n{type(node.op).__name__}"
        else:
            label = type(node).__name__

        dot.node(node_id, label)

        if parent_id:
            dot.edge(parent_id, node_id)

        for child in ast.iter_child_nodes(node):
            add_node(child, node_id)

    add_node(tree.body)
    dot.render("ast_tree", format="png", view=True)
    print("Saved as ast_tree.png")

# visualize_ast("2 + 3 * 4")
# visualize_ast("(100 + 50) * 2 / 3")
# visualize_ast("-5 + 3 * 2")
# visualize_ast("2 ** 10 - 1")





# to visualize the AST  in readable format
import pprint


code = '''
def greet(name):
    print("Hello", name + "!")

greet("John")
'''

tree = ast.parse(code)
pprint.pprint(ast.dump(tree)) 
"""
(.venv) salmanmammadli@pop-os:~/ai-agent-api$ /home/salmanmammadli/ai-agent-api/.venv/bin/python /home/salmanmammadli/ai-agent-api/agent/tools/calculator.py
("Module(body=[FunctionDef(name='greet', args=arguments(posonlyargs=[], "
 "args=[arg(arg='name')], kwonlyargs=[], kw_defaults=[], defaults=[]), "
 "body=[Expr(value=Call(func=Name(id='print', ctx=Load()), "
 "args=[Constant(value='Hello'), BinOp(left=Name(id='name', ctx=Load()), "
 "op=Add(), right=Constant(value='!'))], keywords=[]))], decorator_list=[], "
 "type_params=[]), Expr(value=Call(func=Name(id='greet', ctx=Load()), "
 "args=[Constant(value='John')], keywords=[]))], type_ignores=[])")
"""

