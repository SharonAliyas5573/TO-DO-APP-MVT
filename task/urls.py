from django.urls import path
from . import views

urlpatterns = [
    
    path('tasks/list/', views.task_list, name='task_list'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:id>/', views.task_id, name='task_id'),
    path('tasks/<int:id>/update/', views.task_update, name='task_update'),
    path('tasks/<int:id>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:id>/complete/', views.task_complete, name='task_complete'),
]