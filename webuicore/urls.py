from django.urls import path

from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('uploader/', views.uploader, name='upload'),
    path('mainshow/', views.mainshow, name='mainshow'),
    path('get-files/', views.get_files, name='get_files'),
    path('get-files-detail/', views.get_files_detail, name='get_files_detail'),
    path('execute-anomaly-detection/', views.exe_vad, name='execute_anomaly_detection'),
    path('delete-record/', views.delete_record, name='delete_record'),
    path('delete-record-abnormal/', views.delete_record_abnormal, name='delete_record_abnormal'),
    path('delete-file/', views.delete_file, name='delete_file'),
    path('get-anomaly-clips/', views.get_anomaly_clips, name='get_anomaly_clips'),
    path('get-video-info/', views.get_video_info, name='get_video_info'),
    path('video-detail/', views.video_detail, name='video_detail'),
    path('abnormal-clips-by-label/<str:label>/', views.abnormal_clips_by_label, name='abnormal_clips_by_label'),
    path('generate-description/', views.generate_video_caption, name='generate_video_caption'),
    path('abnormal-clips-by-score/<str:threshold>/', views.abnormal_clips_by_score, name='abnormal_clips_by_score'),
    path('video-detail/popup-page.html', views.popup_page, name='popup_page'),
    path('modify/', views.modify, name='modify'),
    path('gistest/', views.gistest, name='gistest')
]
