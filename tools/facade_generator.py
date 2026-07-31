import re

to_edit = """
"""

wrapper_name = input("Enter name of facade> ")

variables = []
consts = {}

for line in to_edit.splitlines():
    line = line.strip()

    if "=" not in line:
        continue

    var, value = map(str.strip, line.split("=", 1))

    if re.match(r"[A-Z][A-Z0-9_]*$", var):
        consts[var] = value
    else:
        if var not in variables:
            variables.append(var)


class_name = wrapper_name.title().replace(" ", "")

print(f"class {class_name}:")

init_params = ", ".join(["self", *variables])
print(f"    def __init__({init_params}):")

print("        # Constants")
for const, value in consts.items():
    print(f"        self.{const} = {value}")

print("\n        # Variables")
for var in variables:
    print(f"        self.{var} = {var}")

print()
print(f"{wrapper_name.lower()} = {class_name}({', '.join(variables)})")