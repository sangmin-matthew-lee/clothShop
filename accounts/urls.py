from django.urls import path
from . import views

urlpatterns = [
    path('shopping/login/', views.login_view, name='login'),
    path('shopping/register/', views.register_view, name='register'),
    path('shopping/logout/', views.logout_view, name='logout'),
]
