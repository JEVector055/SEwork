from django.contrib.auth.models import AbstractUser
from django.db import models


class Monitor(models.Model):
    monitor_id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    location = models.CharField(max_length=255)


class SourceVideo(models.Model):
    source_id = models.AutoField(primary_key=True)
    monitor_id = models.IntegerField()
    title = models.CharField(max_length=255)
    save_path = models.FileField(max_length=255, upload_to='SourceVideos/')
    upload_time = models.DateTimeField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        """
        返回源视频的标题，以便在交互界面中更容易识别对象。
        """
        return f"Source Video: {self.title}"


class AbnormalClip(models.Model):
    abnormal_id = models.AutoField(primary_key=True)
    source = models.ForeignKey(SourceVideo, on_delete=models.CASCADE)
    save_path = models.FileField(max_length=255, upload_to='SourceVideos/')
    title = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    caption = models.CharField(max_length=255)
    score = models.FloatField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        """
        返回异常视频的标题，以便在交互界面中更容易识别对象。
        """
        return f"Abnormal Video: {self.title}"



class User(AbstractUser):
    class Meta:
        db_table = 'webuicore_user'  # 自定义表名
