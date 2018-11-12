#!/usr/bin/env python3

with open("README.md", "r") as f:
    help_left = f.read().split('The following tests are contained in tests.zip:')[0] + 'The following tests are contained in tests.zip:' + '\n'
with open("README.md", "r") as f:
    help_right = '##' + '##'.join(f.read().split('The following tests are contained in tests.zip:')[1].split('##')[1:])

docs = ""
with open("tests.py", "r") as t:
    t_classes = t.read().split("class ")[1:]
    for t_class in t_classes:
        docs += '* ' + t_class.split('(')[0] + '\n'
        t_methods = t_class.split(":")[1:]
        for t_method in t_methods:
            if len(t_method.split('def ')) > 1:
                method_name = t_method.split('def ')[1].split('(')[0]
                if method_name[:4] == "test":
                    docs += '  - ' + method_name + '\n'

for to_write in ["README.md", "README.txt"]:
    with open(to_write, "w") as f:
        f.write(help_left)
        f.write(docs + '\n')
        f.write(help_right)
