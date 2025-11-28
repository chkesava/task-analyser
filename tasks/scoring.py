from datetime import date, datetime

def calculate_task_score(task):
    score = 0
    explanation = []

    due_date = task.get("due_date")
    if not due_date:
        return 0, "Missing due_date."
    if isinstance(due_date, str):
        try:
            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
        except ValueError:
            return 0, "Invalid date format."
    today = date.today()
    days_left = (due_date - today).days

    if days_left < 0:
        score += 100; explanation.append("Task is overdue.")
    elif days_left <= 3:
        score += 60; explanation.append("Due soon (≤3 days).")
    elif days_left <= 7:
        score += 30; explanation.append("Due this week.")
    else:
        score += 10; explanation.append("Low urgency.")

    importance = int(task.get("importance", 5))
    score += importance * 5
    explanation.append(f"Importance adds {importance * 5}.")

    hours = float(task.get("estimated_hours", 1))
    if hours <= 2:
        score += 15; explanation.append("Quick win bonus.")
    elif hours > 8:
        score -= 10; explanation.append("High effort penalty.")

    if task.get("dependencies"):
        score += 20; explanation.append("Has dependencies (blocks others).")

    return score, " ".join(explanation)
