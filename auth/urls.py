from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
import TO_DO_MVT.settings as settings
urlpatterns = [
    path('login/', views.login, name='login'),
    path('logout/', LogoutView.as_view(next_page=settings.LOGOUT_REDIRECT_URL), name='logout'),
    path('register/', views.register, name='register')
]