from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from .models import Task
from django.utils import timezone
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.dateparse import parse_datetime



@login_required
def task_list(request):
    queryset = Task.objects.filter(user=request.user)
    status = request.GET.get('status', None)
    priority = request.GET.get('priority', None)
    
    if status is not None:
        if status == 'completed':
            queryset = queryset.filter(completed=True)
        elif status == 'expired':
            queryset = queryset.filter(deadline__lt=timezone.now())
        elif status == 'active':
            queryset = queryset.filter(completed=False, deadline__gte=timezone.now())
    
    if priority is not None:
        priorities = priority.split(',')
        queryset = queryset.filter(priority__in=priorities)

    return render(request, 'task_list.html', {'tasks': queryset.order_by('-deadline')})

@csrf_exempt
@login_required
def task_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        if not all(key in data for key in ('title', 'description', 'deadline', 'priority', 'completed')):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        data['deadline'] = parse_datetime(data['deadline'])
        if data['deadline'] is None:
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        data['user'] = request.user
        task = Task.objects.create(**data)

        return JsonResponse({'message': 'Task created successfully'}, status=201)
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)

@csrf_exempt
@login_required
def task_update(request, id):
    task = Task.objects.get(id=id)
    if task.deadline < timezone.now():
        raise ValidationError('Cannot edit an expired task')

    if request.method == 'POST':
        data = json.loads(request.body)

        if not all(key in data for key in ('title', 'description', 'deadline', 'priority', 'completed')):
            return JsonResponse({'error': 'All fields are required'}, status=400)

        data['deadline'] = parse_datetime(data['deadline'])
        if data['deadline'] is None:
            return JsonResponse({'error': 'Invalid date format'}, status=400)

        for key, value in data.items():
            setattr(task, key, value)
        task.save()

        return JsonResponse({'message': 'Task updated successfully'}, status=200)
    else:
        task_data = {
            'title': task.title,
            'description': task.description,
            'deadline': task.deadline.isoformat(),
            'priority': task.priority,
            'completed': task.completed
        }
        return JsonResponse(task_data, status=200)
    

@login_required
def task_delete(request, id):
    task = Task.objects.get(id=id)
    task.delete()
    return redirect('task_list')

