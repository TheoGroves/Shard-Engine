import re

def snake_case(text):
    text = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", text)
    text = re.sub(r"[\s\-]+", "_", text)
    return text.lower()

to_edit = """"""

generate_header = input("h/b: ").strip().lower() == "h" 

for line in to_edit.splitlines():
    line = line.strip()

    if "(" not in line or not line.endswith(")"):
        continue

    before, args = line[:-1].split("(", 1)
    return_type, qualified_name = before.rsplit(" ", 1)
    scope, func_name = qualified_name.rsplit("::", 1)

    if generate_header:
        print(f"{return_type} {func_name}({args});")
    else:
        print(f'.def("{snake_case(func_name)}", &{scope}::{func_name})')