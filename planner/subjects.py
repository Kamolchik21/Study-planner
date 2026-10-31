def add_subject(data, name):
    name = name.strip()
    if not name:
        raise ValueError("Subject name cannot be empty.")
    if name.lower() in [s.lower() for s in data["subjects"]]:
        raise ValueError("This subject already exists.")
    data["subjects"].append(name)


def remove_subject(data, name):
    if name not in data["subjects"]:
        raise ValueError("Subject not found.")
    for task in data["tasks"]:
        if task["subject"] == name and not task["done"]:
            raise ValueError("This subject still has unfinished tasks. Finish or delete them first.")
    data["subjects"].remove(name)
