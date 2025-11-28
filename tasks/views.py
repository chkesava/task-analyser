from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .scoring import calculate_task_score

@csrf_exempt
def analyze_tasks(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)
    if not isinstance(data, list):
        return JsonResponse({"error": "Expected a list of tasks"}, status=400)

    results = []
    for t in data:
        score, reason = calculate_task_score(t)
        t["priority_score"] = score
        t["reason"] = reason
        results.append(t)

    results.sort(key=lambda x: x["priority_score"], reverse=True)
    return JsonResponse(results, safe=False)

def suggest_tasks(request):
    sample = [
        {"title":"Fix login bug","due_date":"2025-11-30","importance":8,"estimated_hours":3,"dependencies":[]},
        {"title":"Write docs","due_date":"2025-12-03","importance":6,"estimated_hours":1,"dependencies":[]},
        {"title":"Refactor API","due_date":"2025-12-05","importance":7,"estimated_hours":5,"dependencies":[]},
    ]
    scored=[]
    for s in sample:
        sc, reason = calculate_task_score(s)
        s["priority_score"]=sc; s["reason"]=reason
        scored.append(s)
    scored.sort(key=lambda x:x["priority_score"],reverse=True)
    return JsonResponse(scored[:3],safe=False)
