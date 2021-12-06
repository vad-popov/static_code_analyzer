import ast

#tree = ast.parse(code)
tree = ast.parse('import str')

# put your code here
for i in ast.walk(tree):
    if isinstance(i, ast.Import):
        for a in i.names:
            print(a.name)
            print(ast.get_source_segment('import str', i))
