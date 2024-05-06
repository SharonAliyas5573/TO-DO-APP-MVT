from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login as auth_login , authenticate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return JsonResponse({'error': 'Username and password are required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(username=username, password=password)
        
        
        return redirect('login')  
    else:
        return render(request, 'base.html')

@csrf_exempt
def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return redirect('task_list')  
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=400)
    else:
        return render(request, 'login.html')
    
def logout(request):
    request.user.logout()
    return redirect('login')  