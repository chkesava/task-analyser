from rest_framework.decorators import api_view
from rest_framework.response import Response
from datetime import date, datetime

# temporary memory cache for the latest analyzed tasks
latest_analyzed_tasks = []


def calculate_task_score(task):
    """Compute a score and reason text for a given task."""
    today = date.today()

    try:
        due_date = datetime.strptime(task.get("due_date"), "%Y-%m-%d").date()
    except Exception:
        return 0, "Invalid due date."

    days_left = (due_date - today).days
    importance = int(task.get("importance", 5))
    estimated_hours = int(task.get("estimated_hours", 1))
    dependencies = task.get("dependencies", [])

    score = 0
    reason = []

    # urgency
    if days_left < 0:
        score -= 20
        reason.append("Past due task (-20).")
    elif days_left <= 3:
        score += 60
        reason.append("Due soon (≤3 days).")
    elif days_left <= 7:
        score += 40
        reason.append("Due this week.")
    else:
        score += 20
        reason.append("Due later.")

    # importance
    score += importance * 5
    reason.append(f"Importance adds {importance * 5}.")

    # effort
    if estimated_hours <= 2:
        score += 10
        reason.append("Quick win bonus.")
    elif estimated_hours > 8:
        score -= 10
        reason.append("Long task penalty.")

    # dependencies
    if dependencies:
        score -= 10
        reason.append("Has dependencies (-10).")

    return score, " ".join(reason)


@api_view(["POST"])
def analyze_tasks(request):
    """Analyze and score given tasks."""
    global latest_analyzed_tasks

    # clear previous analysis to avoid returning stale results
    try:
        latest_analyzed_tasks.clear()
    except Exception:
        # if it's not a list for some reason, fallback to fresh list
        latest_analyzed_tasks = []

    tasks = request.data
    if not isinstance(tasks, list):
        return Response({"error": "Expected a list of tasks."}, status=400)

    analyzed = []
    for task in tasks:
        score, reason = calculate_task_score(task)
        task["priority_score"] = score
        task["reason"] = reason
        analyzed.append(task)

    # sort by score descending
    analyzed.sort(key=lambda t: t["priority_score"], reverse=True)

    # store in memory for suggest endpoint
    latest_analyzed_tasks = analyzed

    return Response(analyzed)


@api_view(["GET"])
def suggest_tasks(request):

    """Return top 3 tasks from the latest analyzed set."""
    if not latest_analyzed_tasks:
        return Response({"error": "No tasks analyzed yet."}, status=400)

    top_tasks = latest_analyzed_tasks[:3]
    return Response(top_tasks)
