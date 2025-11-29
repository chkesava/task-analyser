
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Task
from .scoring import calculate_task_score, detect_cycles, DEFAULT_WEIGHTS


def build_weights_from_request(request):
    """
    Allow simple tuning via query params, e.g.
      /api/tasks/analyze/?importance_weight=6&quick_win_bonus=15
    If not provided, defaults are used.
    """
    weights = DEFAULT_WEIGHTS.copy()
    params = request.GET

    for key in [
        "importance_weight",
        "quick_win_bonus",
        "high_effort_penalty",
        "dependency_bonus",
        "overdue_bonus",
        "due_soon_bonus",
        "due_week_bonus",
        "low_urgency_bonus",
    ]:
        if key in params:
            try:
                weights[key] = int(params[key])
            except ValueError:
                pass

    return weights


@csrf_exempt
def analyze_tasks(request):
    """
    POST /api/tasks/analyze/

    Accepts a JSON array of tasks, validates and scores each one,
    saves valid tasks into the database, and returns them sorted by
    priority_score (highest first).
    """
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    if not isinstance(data, list):
        return JsonResponse({"error": "Expected a JSON array of tasks"}, status=400)

    # Give each task a temporary ID if it doesn't have one (used for cycle detection)
    for idx, t in enumerate(data):
        if "id" not in t:
            t["id"] = idx + 1

    weights = build_weights_from_request(request)
    cycles = detect_cycles(data)

    results = []

    for raw_task in data:
        task_id = raw_task.get("id")
        in_cycle = task_id in cycles

        score, reason, is_valid = calculate_task_score(
            raw_task, weights=weights, in_cycle=in_cycle
        )

        out = {
            "id": task_id,
            "title": raw_task.get("title"),
            "due_date": raw_task.get("due_date"),
            "importance": raw_task.get("importance"),
            "estimated_hours": raw_task.get("estimated_hours"),
            "dependencies": raw_task.get("dependencies") or [],
            "priority_score": score,
            "reason": reason,
            "valid": is_valid,
        }

        if is_valid:
            obj, created = Task.objects.update_or_create(
                title=out["title"],
                due_date=out["due_date"],
                defaults={
                    "importance": out["importance"] or 5,
                    "estimated_hours": out["estimated_hours"] or 1,
                    "dependencies": out["dependencies"],
                    "last_score": score,
                    "last_reason": reason,
                },
            )
            out["db_id"] = obj.id
        else:
            out["db_id"] = None

        results.append(out)

    results.sort(key=lambda t: t["priority_score"], reverse=True)
    return JsonResponse(results, safe=False)


def suggest_tasks(request):
    """
    GET /api/tasks/suggest/

    Reads tasks from the database, recomputes their scores (to keep
    urgency up to date), and returns the top 3 tasks with explanations.
    """
    weights = build_weights_from_request(request)

    qs = Task.objects.all()
    raw_tasks = []

    for t in qs:
        raw_tasks.append(
            {
                "id": t.id,
                "title": t.title,
                "due_date": t.due_date.isoformat(),
                "importance": t.importance,
                "estimated_hours": t.estimated_hours,
                "dependencies": t.dependencies,
            }
        )

    cycles = detect_cycles(raw_tasks)

    scored = []
    for raw in raw_tasks:
        in_cycle = raw["id"] in cycles
        score, reason, is_valid = calculate_task_score(
            raw, weights=weights, in_cycle=in_cycle
        )
        if not is_valid:
            # Skip invalid stored records (should be rare)
            continue

        scored.append(
            {
                "id": raw["id"],
                "title": raw["title"],
                "due_date": raw["due_date"],
                "importance": raw["importance"],
                "estimated_hours": raw["estimated_hours"],
                "dependencies": raw["dependencies"],
                "priority_score": score,
                "reason": reason,
            }
        )

    scored.sort(key=lambda t: t["priority_score"], reverse=True)
    top3 = scored[:3]
    return JsonResponse(top3, safe=False)
