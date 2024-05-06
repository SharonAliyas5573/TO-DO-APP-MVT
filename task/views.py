from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import Task
from django.utils import timezone
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime
from django.http import HttpResponse
from .serializers import TaskSerializer


@csrf_exempt
@login_required
def task_id(request, id=None):
    if id is not None:
        task = Task.objects.get(id=id)
        serializer = TaskSerializer(task)
        return JsonResponse(serializer.data)



@csrf_exempt
@login_required
def task_list(request):
    status = request.GET.get("status", "All")
    priority = request.GET.get("priority", "All")
    tasks = Task.objects.filter(user=request.user)

    if status != "All":
        if status == "completed":
            tasks = tasks.filter(completed=True)
        elif status == "expired":
            tasks = tasks.filter(deadline__lt=timezone.now())
        elif status == "active":
            tasks = tasks.filter(completed=False, deadline__gte=timezone.now())

    if priority != "All":
        tasks = tasks.filter(priority=priority)

    tasks = tasks.order_by("-deadline")
    serializer = TaskSerializer(tasks, many=True)
    return render(request, "todo_list.html", {"tasks": serializer.data})

@csrf_exempt
@login_required
def task_create(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        deadline = request.POST.get("deadline")
        priority = request.POST.get("priority")

        if not all([title, description, deadline, priority]):
            return JsonResponse({"error": "All fields are required"}, status=400)

        deadline = parse_datetime(deadline)
        if deadline is None:
            return JsonResponse({"error": "Invalid date format"}, status=400)

        task = Task.objects.create(
            title=title,
            description=description,
            deadline=deadline,
            priority=priority,
            completed=False,
            user=request.user,
        )

        return JsonResponse({"success": True, "message": "Task created successfully"})
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"})


@csrf_exempt
@login_required
def task_update(request, id):
    try:
        task = Task.objects.get(id=id)
    except Task.DoesNotExist:
        return JsonResponse({"error": "Task does not exist"}, status=404)

    if task.deadline < timezone.now():
        raise ValidationError("Cannot edit an expired task")

    if request.method == "POST":
        data = json.loads(request.body)
        try:
            data = json.loads(request.body)
            if "deadline" in data:
                data["deadline"] = parse_datetime(data["deadline"])
            if data["deadline"] is None:
                return JsonResponse({"error": "Invalid date format"}, status=400)

            for key, value in data.items():
                setattr(task, key, value)
            task.save()
            return JsonResponse(data, status=200)
        except Exception as e:
                return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


@csrf_exempt
@login_required
def task_complete(request, id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            completed = data.get('completed', False)  # Default to False if 'completed' is not provided
            task = Task.objects.get(id=id)
            task.completed = completed
            task.save()
            return JsonResponse({"message": "Task marked as complete"}, status=200)
        except Task.DoesNotExist:
            return JsonResponse({"error": "Task does not exist"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)
    
    
@login_required
def task_delete(request, id):
    task = Task.objects.get(id=id)
    task.delete()
    return redirect("task_list")
