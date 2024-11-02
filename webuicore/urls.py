from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    # path('logout/', views.user_logout, name='logout'),
    path('uploader/', views.uploader, name='upload'),
    path('current/', views.currentresult, name='current'),
    path('execute_command/', views.ExecuteCommandView.as_view(), name='execute_command'),
    path('mainshow/', views.mainshow, name='mainshow'),
    path('get-files/', views.get_files, name='get_files'),
    path('execute-anomaly-detection/', views.execute_anomaly_detection, name='execute_anomaly_detection'),
]
