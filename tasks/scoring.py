# tasks/scoring.py
from datetime import date, datetime

DEFAULT_WEIGHTS = {
    "importance_weight": 5,
    "quick_win_bonus": 10,
    "high_effort_penalty": 10,
    "dependency_bonus": 20,
    "overdue_bonus": 100,
    "due_soon_bonus": 60,
    "due_week_bonus": 30,
    "low_urgency_bonus": 10,
}


def normalize_date(d):
    """Accept 'YYYY-MM-DD' string or date object and return a date."""
    if isinstance(d, date):
        return d
    if isinstance(d, str):
        return datetime.strptime(d, "%Y-%m-%d").date()
    raise ValueError("Invalid date type")


def detect_cycles(tasks):
    """
    Detect circular dependencies based on an 'id' field in each task dict.
    dependencies are assumed to be a list of IDs.
    Returns a set of task IDs that are part of at least one cycle.
    """
    graph = {}
    for t in tasks:
        tid = t.get("id")
        if tid is None:
            continue
        deps = t.get("dependencies") or []
        graph[tid] = deps

    visited = {}
    in_cycle = set()

    def dfs(node, stack):
        state = visited.get(node)
        if state == "visiting":
            # we found a cycle, add all nodes in this cycle segment
            in_cycle.update(stack[stack.index(node):])
            return
        if state == "done":
            return

        visited[node] = "visiting"
        stack.append(node)
        for nei in graph.get(node, []):
            if nei in graph:
                dfs(nei, stack)
        stack.pop()
        visited[node] = "done"

    for node in graph.keys():
        if visited.get(node) is None:
            dfs(node, [])

    return in_cycle


def calculate_task_score(task, weights=None, in_cycle=False):
    """
    Validate and score a task.
    Returns: (score, explanation, is_valid)

    If invalid:
      - score = 0
      - explanation contains error message
      - is_valid = False
    """
    if weights is None:
        weights = DEFAULT_WEIGHTS

    explanations = []
    score = 0

    # ----- Required fields -----
    title = task.get("title")
    if not title:
        return 0, "Missing title.", False

    due_raw = task.get("due_date")
    if not due_raw:
        return 0, "Missing due_date.", False

    try:
        due_date = normalize_date(due_raw)
    except ValueError:
        return 0, "Invalid due_date format. Use YYYY-MM-DD.", False

    # importance
    try:
        importance = int(task.get("importance", 5))
    except (TypeError, ValueError):
        importance = 5
        explanations.append("Importance invalid, defaulted to 5.")

    # effort
    try:
        hours = int(task.get("estimated_hours", 1))
    except (TypeError, ValueError):
        hours = 1
        explanations.append("Estimated hours invalid, defaulted to 1.")

    # ----- Urgency -----
    today = date.today()
    days_left = (due_date - today).days

    if days_left < 0:
        score += weights["overdue_bonus"]
        explanations.append("Task is overdue (very urgent).")
    elif days_left <= 3:
        score += weights["due_soon_bonus"]
        explanations.append("Due soon (<=3 days).")
    elif days_left <= 7:
        score += weights["due_week_bonus"]
        explanations.append("Due within this week.")
    else:
        score += weights["low_urgency_bonus"]
        explanations.append("Low urgency (more than a week away).")

    # ----- Importance -----
    score += importance * weights["importance_weight"]
    explanations.append(
        f"Importance {importance} weighted by {weights['importance_weight']}."
    )

    # ----- Effort -----
    if hours < 2:
        score += weights["quick_win_bonus"]
        explanations.append("Quick win (low effort) bonus.")
    elif hours > 8:
        score -= weights["high_effort_penalty"]
        explanations.append("High effort penalty.")

    # ----- Dependencies -----
    deps = task.get("dependencies") or []
    if isinstance(deps, list) and deps:
        score += weights["dependency_bonus"]
        explanations.append("Has dependencies (may unblock other work).")

    # ----- Circular dependency note -----
    if in_cycle:
        explanations.append("Warning: task is in a circular dependency chain.")

    explanation = " ".join(explanations)
    return score, explanation, True
