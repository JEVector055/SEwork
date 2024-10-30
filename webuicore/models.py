from django.db import models
# myapp/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
class VideoClip(models.Model):
    """
    视频剪辑模型，用于存储视频剪辑的相关信息。
    """
    title = models.CharField(max_length=200)  # 视频剪辑的标题，最大长度为200字符
    VideoClip_file = models.FileField(upload_to='VideoClips/')  # 视频剪辑文件上传路径
    created_at = models.DateTimeField(auto_now_add=True)  # 视频剪辑的创建时间，自动设置为记录创建时的时间

    def __str__(self):
        """
        返回视频剪辑的标题，以便在交互界面中更容易识别对象。
        """
        return self.title

class ClipComment(models.Model):
    """
    视频剪辑评论模型，用于存储与视频剪辑相关的评论。
    """
    video = models.OneToOneField(VideoClip, on_delete=models.CASCADE)  # 与VideoClip模型建立一对一关系
    text = models.TextField(blank=True, null=True)  # 评论的文本内容，允许为空
    textbackup = models.TextField(blank=True, null=True)  # 评论文本的备份，用于存储预处理后的文本，允许为空

    def __str__(self):
        """
        返回评论所属视频剪辑的标题，以便在交互界面中更容易识别对象。
        """
        return f"Comment for {self.video.title}"

class SourceVideo(models.Model):
    """
    源视频模型，用于存储源视频的相关信息。
    """
    title = models.CharField(max_length=200)  # 源视频的标题，最大长度为200字符
    SourceVideo_file = models.FileField(upload_to='SourceVideos/')  # 源视频文件上传路径
    uploaded_at = models.DateTimeField(auto_now_add=True)  # 源视频的上传时间，自动设置为记录创建时的时间

    def __str__(self):
        """
        返回源视频的标题，以便在交互界面中更容易识别对象。
        """
        return f"Source Video: {self.title}"


from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    # 你可以在这里添加额外的字段
    pass

    class Meta:
        db_table = 'webuicore_user'  # 如果你需要自定义表名

    # 重新定义 groups 和 user_permissions 字段，设置 related_name
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='webuicore_user_set',
        related_query_name='webuicore_user'
    )

    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='webuicore_user_set',
        related_query_name='webuicore_user'
    )

