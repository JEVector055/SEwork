from django.shortcuts import render,redirect
from django.conf import settings
from django.http import Http404
from .models import VideoClip,SourceVideo,ClipComment
from .forms import UploadUnitform
from django.views import View
import subprocess
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm
# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout
from django.http import FileResponse
from django.http import JsonResponse
import os
def get_files(request):
    # 假设文件存储在MEDIA_ROOT目录下
    media_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media','SourceVideos')
    files = os.listdir(media_root)
    return JsonResponse(files, safe=False)

def download_file(request, filename):
    # 假设文件存储在MEDIA_ROOT目录下
    media_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media')
    file_path = os.path.join(media_root, filename)

    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return HttpResponseNotFound("File not found")

dirs=f"{settings.MEDIA_ROOT}"
dirmp4=f"{settings.MEDIA_ROOT}/anomaly_mp4"
dirr=f"{settings.MEDIA_ROOT}/result.mp4"
dirat=f"{settings.MEDIA_ROOT}/anomaly_txt"
dirxt=f"{settings.MEDIA_ROOT}/final_txt"
extension="mp4"
# myapp/views.py

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')





# def uploader(request):
#     """
#     处理视频上传的视图函数。
#
#     参数:
#     - request: HttpRequest对象，包含用户请求的数据。
#
#     返回:
#     - 如果是POST请求且表单验证通过，则保存上传的视频并重定向到'current'页面。
#     - 如果是GET请求，则渲染上传表单页面。
#     - 如果数据库中存在视频且未上传新视频，则启动视频处理程序。
#     """
#     # 获取数据库中最新的视频对象
#     svideo=SourceVideo.objects.last()
#
#     # 判断是否有待处理的视频
#     if svideo:#判断是否上传
#         # 启动切片程序
#         print("processing1")
#         subprocess.run(f"python save_anomaly_segments.py --smp4 {dirs}/{svideo.title} --amp4dir {dirmp4} --dmp4 {dirr}")
#         return redirect('current')
#     else:
#         # 处理POST请求，即用户提交表单的情况
#         if request.method == 'POST':
#             form=UploadUnitform(request.POST, request.FILES)
#             if form.is_valid():
#                 form.save()
#                 return redirect('current')
#             else:
#                 # 如果表单验证失败，抛出404错误
#                 raise Http404("Wrongtype.")
#         else:
#             # 处理GET请求，即用户请求上传表单的情况
#             form=UploadUnitform()
#             return render(request, 'webuicore/mainpage.html',{
#             'form':form
#             })
def uploader(request):
    """
    处理视频上传的视图函数。

    参数:
    - request: HttpRequest对象，包含用户请求的数据。

    返回:
    - 如果是POST请求且表单验证通过，则保存上传的视频并重定向到'current'页面。
    - 如果是GET请求，则渲染上传表单页面。
    - 如果数据库中存在视频且未上传新视频，则启动视频处理程序。
    """
    # 获取数据库中最新的视频对象
    svideo=SourceVideo.objects.last()
    # 处理POST请求，即用户提交表单的情况
    if request.method == 'POST':
        form=UploadUnitform(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('mainshow')
        else:
            # 如果表单验证失败，抛出404错误
            raise Http404("Wrongtype.")
    else:
        # 处理GET请求，即用户请求上传表单的情况
        form=UploadUnitform()
        return render(request, 'webuicore/mainpage.html',{
        'form':form
        })



def currentresult(request):
    vclips_comments=VideoClip.objects.all().select_related('comment')
    svideo=SourceVideo.objects.last()
    ##将片段信息导入数据库
    ##启动程序（未添加）    
    return render(request, 'webuicore/result.html',{
        'vclips_comments':vclips_comments,
        'svideo':svideo
    })

def mainshow(request):
    """
    加载并渲染主显示页面。

    从数据库中获取所有视频剪辑及其关联的评论，并获取最新的源视频。
    如果最新的源视频存在且有视频文件路径，则获取其URL，否则设置为None。

    参数:
    - request: HTTP 请求对象。

    返回:
    - 渲染后的 'webuicore/result.html' 页面，包含视频剪辑和评论、最新的源视频以及视频URL。
    """
    # 获取所有视频剪辑及其关联的评论
    vclips_comments = VideoClip.objects.all().select_related('comment')

    # 获取数据库中最新的源视频
    svideo = SourceVideo.objects.last()

    # 确保 svideo 存在并且有视频文件路径
    if svideo and svideo.SourceVideo_file:
        # 获取源视频文件的URL
        video_url = svideo.SourceVideo_file.url
    else:
        # 如果源视频或视频文件路径不存在，设置video_url为None
        video_url = None
    print(video_url)

    # 渲染并返回 'webuicore/result.html' 页面
    return render(request, 'webuicore/result.html', {
        'vclips_comments': '',
        'svideo': svideo,
        'video_url': video_url
    })



def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = form.cleaned_data['user']
            login(request, user)
            return redirect('upload')  # 登录成功后重定向到主页
    else:
        form = LoginForm()
    return render(request, r'G:\Code\video_management\webui4VadCLIP-develop\templates\webuicore\login.html', {'form': form})

class ExecuteCommandView(View):
    def post(self, request):
        button_id = request.POST.get('button_id')
        videoclip=VideoClip(id=button_id)
        subprocess.run(f"python create_anomaly_captions.py --index {button_id}")##修改对应后端接口（直接输出到数据库或临时文件）,输出到数据库需要添加索引参数
        subprocess.run(f"torchrun --nproc_per_node=2 --nnodes=1 generate_final_caption.py --index {button_id}")##修改对应后端接口直接输出到数据库或临时文件,需要根据buttonid添加索引参数
        
        

        