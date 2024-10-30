from django import forms
from .models import SourceVideo
from django.contrib.auth.forms import AuthenticationForm
class UploadUnitform(forms.ModelForm):
    class Meta:
        model = SourceVideo
        fields = ['title', 'SourceVideo_file']

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

def play_video(request, video_id):
    video = ProcessedVideo.objects.get(id=video_id)
    return render(request, 'play_video.html', {'video': video})