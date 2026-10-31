from planner.tasks import task_minutes
from planner.utils import days_left, describe_days, format_minutes


def format_task(task):
    when = describe_days(days_left(task["deadline"]))
    return f"{task['title']}  [{task['subject']}]  {format_minutes(task_minutes(task))}  - {when}"


def fill_listbox(listbox, lines):
    listbox.delete(0, "end")
    for line in lines:
        listbox.insert("end", line)


def set_text(widget, text):
    widget.configure(state="normal")
    widget.delete("1.0", "end")
    widget.insert("1.0", text)
    widget.configure(state="disabled")
