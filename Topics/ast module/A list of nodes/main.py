import ast

expression = "(34 + 6) * (23**2 - 7 + 45**2)"

# put your code here
tree = ast.parse(expression)
# nodes = [type(i).__name__ for i in ast.walk(tree)]
nodes = list(ast.walk(tree))
print(len(nodes))
