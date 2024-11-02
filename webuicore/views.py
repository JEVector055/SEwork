import os
import subprocess

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.http import FileResponse, JsonResponse, HttpResponseNotFound
from django.http import Http404
from django.shortcuts import render, redirect
from django.views import View

from .forms import LoginForm, RegisterForm, UploadUnitform
from .models import VideoClip, SourceVideo, User

def get_files(request):
    # 假设文件存储在MEDIA_ROOT目录下
    media_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'media', 'SourceVideos')
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


dir = f"{settings.MEDIA_ROOT}"
dir_sour = f"{settings.MEDIA_ROOT}/anomaly_mp4"
dir_res = f"{settings.MEDIA_ROOT}/result.mp4"
dir_at = f"{settings.MEDIA_ROOT}/anomaly_txt"
dir_xt = f"{settings.MEDIA_ROOT}/final_txt"
extension = "mp4"


def user_register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'webuicore/user_register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'webuicore/user_login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


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
    SourceVideo.objects.last()
    # 处理POST请求，即用户提交表单的情况
    if request.method == 'POST':
        form = UploadUnitform(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('mainshow')
        else:
            # 表单验证失败，抛出404错误
            raise Http404("Wrongtype.")
    else:
        # 处理GET请求，即用户请求上传表单的情况
        form = UploadUnitform()
        return render(request, 'webuicore/mainpage.html', {'form': form})


def currentresult(request):
    vclips_comments = VideoClip.objects.all().select_related('comment')
    svideo = SourceVideo.objects.last()
    ##将片段信息导入数据库
    ##启动程序（未添加）    
    return render(request, 'webuicore/result.html', {
        'vclips_comments': vclips_comments,
        'svideo': svideo
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
    VideoClip.objects.all().select_related('comment')

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
            # 从表单中获取用户名和密码
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # 使用 authenticate 验证用户名和密码
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # 验证通过，登录用户并重定向到 /mainshow
                login(request, user)
                return redirect('/mainshow')
            else:
                # 验证失败，返回错误信息
                form.add_error(None, "用户名或密码不正确")
    else:
        form = LoginForm()
    return render(request, 'webuicore/user_login.html', {'form': form})
# CREATE TABLE `django_session` (
#     `session_key` varchar(40) NOT NULL PRIMARY KEY,
#     `session_data` text NOT NULL,
#     `expire_date` datetime NOT NULL
# ) ENGINE=InnoDB;


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 获取表单数据
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # username=form.cleaned_data['username'],
            # password=form.cleaned_data['password']

            # 使用自定义 User 模型创建新用户
            User.objects.create_user(username=username, password=password)
            return redirect('login')  # 注册成功后重定向到登录页面
    else:
        form = RegisterForm()

    return render(request, 'webuicore/user_register.html', {'form': form})


class ExecuteCommandView(View):
    def post(self, request):
        button_id = request.POST.get('button_id')
        VideoClip(id=button_id)
        subprocess.run(f"python create_anomaly_captions.py --index {button_id}")
        # 修改对应后端接口（直接输出到数据库或临时文件）,输出到数据库需要添加索引参数
        subprocess.run(f"torchrun --nproc_per_node=2 --nnodes=1 generate_final_caption.py --index {button_id}")
        # 修改对应后端接口直接输出到数据库或临时文件,需要根据buttonid添加索引参数


import json, logging, cv2, tqdm, torch
from PIL import Image
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


@csrf_exempt
def execute_anomaly_detection(request):
    if request.method == 'POST':
        try:
            print('Received POST request', request)
            # 尝试解析请求体
            data = json.loads(request.body.decode('utf-8'))
            # print(data)
            video_src = data.get('video_url')
            # print(video_src)
            if not video_src:
                return JsonResponse({'error': 'video_src is required'}, status=400)

            # 处理正常逻辑
            # 例如，调用异常检测函数
            result = detect_anomalies(video_src)
            # result = {'status': 'success', 'message': 'Anomaly detection executed'}

            return JsonResponse(result, safe=False)
        except json.JSONDecodeError as e:
            logger.error(f'Invalid JSON format: {e}')
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            logger.error(f'Unexpected error: {e}')
            return JsonResponse({'error': 'Internal server error'}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


def detect_anomalies(video_src):
    # 这里实现你的异常检测逻辑
    # 假设返回一个包含异常片段的列表
    # 每个片段包含 title 和 file 字段
    """
        处理视频帧，识别并保存异常片段。

        参数:
        video_path: str, 输入视频文件的路径。
        output_dir: str, 输出异常片段的保存目录。

        返回:
        list, 包含所有异常片段保存路径的列表。
        """
    input_video_path = os.path.join('G:/Code/video_management/webui4VadCLIP-develop', video_src)
    input_video_path = 'G:/Code/video_management/webui4VadCLIP-develop/media/SourceVideos/demo_video_lZ4NRGw.mp4'
    print(input_video_path)  # 为什么不能读取mediaroot
    output_dir = input_video_path
    # 创建输出目录（如果不存在）
    # os.makedirs(output_dir, exist_ok=True)
    # 打开视频文件
    cap = cv2.VideoCapture(input_video_path)

    # 获取视频的总帧数和帧率
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"Total Frames: {frame_count}, FPS: {fps}")
    # 创建一个tqdm进度条
    progress_bar = tqdm(total=frame_count, desc="Processing Frames", unit="frame")

    # 定义视频中可能的异常行为标签
    labels = ["Normal", "Abuse", "Arrest", "Arson", "Assault", "Burglary", "Explosion", "Fighting",
              "Road Accidents", "Robbery", "Shooting", "Shoplifting", "Stealing", "Vandalism"]

    video_features_list = []  # 帧级标签集合
    video_frame_list = []
    anomaly_frames = []  # 异常帧
    anomaly_start_frame = None  # 起始位置
    anomaly_captions = []  # 用于存储异常帧的描述
    anomaly_segment_paths = []  # 存储异常片段的路径列表
    segment_dir = None
    i = 0
    while True:
        i += 1
        print(i)
        ret, frame = cap.read()
        if not ret:
            break
        video_frame_list.append(frame)

        with torch.no_grad():
            frame_pil = Image.fromarray(frame)
            frame_preprocessed = clip_preprocess(frame_pil).unsqueeze(0).to(device_0)
            frame_features = clip_model.encode_image(frame_preprocessed)
            video_features_list.append(frame_features)

            if len(video_features_list) >= args.visual_length:
                video_features = torch.cat(video_features_list, dim=0)
                video_features = video_features.reshape(1, 256, 512)
                lengths = torch.tensor([args.visual_length]).to(device_0)
                res = eval_anomaly_scores(clipvad_model, video_features, lengths, device_0)

                for j in range(len(res)):
                    text_score = res[j].item()
                    if text_score > 0.8:
                        label = "Anomaly"
                        color = (0, 0, 255)
                        prompt = generate_label(clip_model, clip_preprocess, video_frame_list[j], labels, device_0)
                        caption = generate_caption(blip_model, blip_processor, video_frame_list[j], prompt, device_1)
                        anomaly_captions.append(caption)  # 保存描述
                        # 更新异常起始帧
                        if anomaly_start_frame is None:
                            anomaly_start_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - len(video_frame_list) + j
                        anomaly_frames.append(video_frame_list[j])
                    else:
                        label = "Normal"
                        color = (0, 255, 0)
                        description = "No anomaly detected"
                        if anomaly_frames:
                            # 更新异常结束帧
                            anomaly_end_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - len(video_frame_list) + j
                            # 将帧转化为实际时间
                            start_time = anomaly_start_frame / fps
                            end_time = anomaly_end_frame / fps

                            # 构建输出文件名
                            segment_dir = f"{output_dir}/anomaly_{start_time:.2f}_{end_time:.2f}"
                            os.makedirs(segment_dir, exist_ok=True)
                            segment_filename = f"{segment_dir}/anomaly_{start_time:.2f}_{end_time:.2f}.mp4"
                            caption_filename = f"{segment_dir}/anomaly_{start_time:.2f}_{end_time:.2f}.txt"

                            # 保存异常片段为视频文件
                            save_frames_as_mp4(anomaly_frames, segment_filename, fps)

                            # 写入描述到文本文件
                            with open(caption_filename, 'w') as file:
                                for caption in anomaly_captions:
                                    file.write(caption + '\n')

                            # 记录异常片段的路径
                            anomaly_segment_paths.append(segment_dir)

                            # 清空异常片段和描述列表
                            anomaly_frames = []
                            anomaly_start_frame = None
                            anomaly_captions = []

                    cv2.putText(video_frame_list[j], f'{label}: {text_score:.2f}', (16, 160), cv2.FONT_HERSHEY_SIMPLEX,
                                1.0, color, 1, cv2.LINE_AA)
                    cv2.putText(video_frame_list[j], f'Description: {description}', (16, 224), cv2.FONT_HERSHEY_SIMPLEX,
                                1.0, color, 1, cv2.LINE_AA)

                video_frame_list = []
                video_features_list = []  # 清空列表以释放显存
                torch.cuda.empty_cache()

            # 更新进度条
            progress_bar.update(1)

        # 视频结束部分异常片段(如果有)
        if anomaly_frames:
            anomaly_end_frame = frame_count
            start_time = anomaly_start_frame / fps
            end_time = anomaly_end_frame / fps
            segment_dir = f"{output_dir}/anomaly_{start_time:.2f}_{end_time:.2f}"
            os.makedirs(segment_dir, exist_ok=True)
            segment_filename = f"{segment_dir}/anomaly_{start_time:.2f}_{end_time:.2f}.mp4"
            caption_filename = f"{segment_dir}/anomaly_{start_time:.2f}_{end_time:.2f}.txt"

            # 保存异常片段为视频文件
            save_frames_as_mp4(anomaly_frames, segment_filename, fps)

            # 写入描述到文本文件
            with open(caption_filename, 'w') as file:
                for caption in anomaly_captions:
                    file.write(caption + '\n')

            # 记录异常片段的路径
            anomaly_segment_paths.append(segment_dir)

    # 关闭进度条
    progress_bar.close()
    cap.release()
    print(anomaly_segment_paths)
    return anomaly_segment_paths


def save_frames_as_mp4(frames, output_filename, fps):
    """
    将帧列表保存为MP4视频文件。

    参数:
    frames: list, 包含帧的列表。
    output_filename: str, 输出视频文件的路径。
    fps: float, 视频的帧率。
    """
    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

    for frame in frames:
        out.write(frame)

    out.release()
