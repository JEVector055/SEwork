from django import forms

from .models import SourceVideo


class UploadUnitform(forms.ModelForm):
    class Meta:
        model = SourceVideo
        fields = ['source_title', 'source_path', 'start_time']  # 移除 'upload_time'

    # 给 'source_title' 字段添加自定义样式
    source_title = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'custom-title-input',
            'placeholder': '请输入视频标题'
        })
        , label='视频标题'
    )

    # 给 'source_path' 字段添加文件上传控件
    source_path = forms.FileField(
        widget=forms.ClearableFileInput(attrs={
            'class': 'custom-file-input',
            'id': 'source-video-file-id'
        })
        , label='文件路径'
    )

    # 给 'start_time' 字段添加自定义样式
    start_time = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'custom-datetime-input',
            'type': 'datetime-local'  # 使用本地日期时间选择器
        })
        , label='开始时间'
    )


# forms.py
from django import forms
from django.contrib.auth import authenticate
from .models import User


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError("用户名或密码错误")
            self.cleaned_data['user'] = user
        return cleaned_data


class RegisterForm(forms.Form):
    username = forms.CharField(max_length=150, label="用户名")
    password = forms.CharField(widget=forms.PasswordInput, label="密码")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="确认密码")

    def clean_username(self):
        username = self.cleaned_data.get('username')
        # 检查用户名是否已存在
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("用户名已被使用")
        return username

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        # 检查两次输入的密码是否匹配
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("两次输入的密码不匹配")

        return cleaned_data

# def play_video(request, video_id):
#     video = ProcessedVideo.objects.get(id=video_id)
#     return render(request, 'play_video.html', {'video': video})
