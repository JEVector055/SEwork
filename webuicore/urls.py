from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    #path('register/', views.register, name='register'),
    #path('login/', login_view, name='login'),
    #path('logout/', views.user_logout, name='logout'),
    path('', views.uploader, name='upload'),
    path('current/', views.currentresult, name='current'),
    path('execute_command/', views.ExecuteCommandView.as_view(), name='execute_command'),
    path('mainshow/', views.mainshow, name='mainshow'),
    path('get-files/', views.get_files, name='get_files'),
]
