import base64
import json
import os
import random
import re
from datetime import datetime, timedelta

import cv2
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import FileResponse, JsonResponse, HttpResponseNotFound
from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from moviepy.video.io.VideoFileClip import VideoFileClip
from openai import OpenAI

from .forms import LoginForm, RegisterForm, UploadUnitform
from .models import SourceVideo, AbnormalClip, User, Monitor
from .save_anomaly_segments.save_anom_segs import det_anom

local_prefix = f"{settings.MEDIA_ROOT}\\"
local_prefix = local_prefix.replace('\\', '/')
def login_view(request):
    print(settings.BASE_DIR)
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
                request.session['from_login'] = True  # 设置session变量
                login(request, user)
                return redirect('/mainshow')
            else:
                # 验证失败，返回错误信息
                form.add_error(None, "用户名或密码不正确")
                return redirect('login')
    else:
        form = LoginForm()

    return render(request, 'webuicore/user_login.html', {'form': form})


def mainshow(request):
    # # 获取所有视频剪辑及其关联的评论
    # VideoClip.objects.all().select_related('comment')
    print("SERVER_PORT:",settings.SERVER_URL)
    # 获取数据库中最新的源视频
    svideo = SourceVideo.objects.last()

    # 确保 svideo 存在并且有视频文件路径
    if svideo and svideo.save_path:
        # 获取源视频文件的URL
        video_url = svideo.save_path
        print('video_url:', video_url)
    else:
        # 如果源视频或视频文件路径不存在，设置video_url为None
        video_url = None
    # 渲染并返回 'webuicore/result.html' 页面
    return render(request, 'webuicore/mainshow.html', {
        'vclips_comments': '',
        'svideo': svideo,
        'video_url': video_url,
        'server_url': settings.SERVER_URL
    })


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 获取表单数据
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            User.objects.create_user(username=username, password=password)
            return redirect('login')  # 注册成功后重定向到登录页面
    else:
        form = RegisterForm()

    return render(request, 'webuicore/user_register.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


def get_files(request):
    # 查询数据库中的 save_path 字段
    files = SourceVideo.objects.values_list('save_path', flat=True)
    # 将 QuerySet 转换为列表
    files_list = list(files)
    return JsonResponse(files_list, safe=False)


def get_files_detail(request):
    # 查询数据库中的 save_path 字段
    files = AbnormalClip.objects.values_list('save_path', flat=True)
    # 将 QuerySet 转换为列表
    files_list = list(files)
    return JsonResponse(files_list, safe=False)


def get_anomaly_clips(request):
    video_url = request.GET.get('video_url')

    if not video_url:
        return JsonResponse({'success': False, 'error': 'No video URL provided'}, status=400)

    try:
        # 正则表达式模式，匹配 http(s)://.../media/
        pattern = r'^https?://[^/]+/media/'

        # 使用正则表达式进行替换
        video_src = re.sub(pattern, local_prefix, video_url)
        video_src = video_src.replace('/', '\\')

        print('video_src', video_src)

        # 查询对应的 SourceVideo 对象并获取 source_id
        source_id = SourceVideo.objects.values_list('source_id', flat=True).get(save_path=video_src)
        print('source_id', source_id)
        # 查询与该视频相关的所有异常片段的 save_path
        anomaly_clips_save_paths = AbnormalClip.objects.filter(source_id=source_id).values_list('save_path', flat=True)

        print('anomaly_clips_save_paths', anomaly_clips_save_paths)

        # 准备返回的数据
        anomaly_clips_data = list(anomaly_clips_save_paths)
        print(anomaly_clips_data)
        return JsonResponse(anomaly_clips_data, safe=False)

    except SourceVideo.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'SourceVideo not found'}, status=404)
    except AbnormalClip.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No abnormal clips found for the given source_id'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def download_file(request, filename):
    # 假设文件存储在MEDIA_ROOT目录下
    media_root = settings.MEDIA_ROOT
    file_path = os.path.join(media_root, filename)

    if os.path.exists(file_path):
        response = FileResponse(open(file_path, 'rb'))
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    else:
        return HttpResponseNotFound("File not found")


def video_detail(request):
    file_path = request.GET.get('file_path')
    if not file_path:
        return render(request, 'error.html', {'message': 'No file path provided.'})

    print('file_path', file_path)

    # 将 file_path 放入字典中
    context = {
        'file_path': file_path,
        'server_url': settings.SERVER_URL
    }

    return render(request, 'webuicore/queryedit.html', context)


@csrf_exempt
def delete_record(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            save_path = data.get('file_path')
            # 查找并删除数据库记录
            file_record = SourceVideo.objects.filter(save_path=save_path).first()
            if file_record:
                file_record.delete()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Record not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


def get_video_info(request):
    print('4')
    video_url = request.GET.get('url')
    print("video_url:",video_url)
    # 正则表达式模式，匹配 http(s)://.../media/
    pattern = r'^https?://[^/]+/media/'

    # 使用正则表达式进行替换
    video_src = re.sub(pattern,'media/', video_url)
    video_src = video_src.replace('\\', '/')

    print('video_src', video_src)

    try:
        # 根据视频文件名查找对应的异常片段
        clip = AbnormalClip.objects.filter(save_path=video_src).first()

        print('clip:', clip)

        # 构建响应数据
        data = {
            "anomalies": []
        }

        # 起始时间和截止时间保留整秒数
        start_time = clip.start_time.replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')
        end_time = clip.end_time.replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')

        # 异常得分保留两位小数
        score = f"{clip.score:.2f}"

        data['anomalies'].append({
            "source_id": clip.source_id,
            "id": clip.abnormal_id,
            "title": clip.title,
            "start_time": start_time,
            "end_time": end_time,
            "Label": clip.label,
            "score": score,
            "Caption": clip.caption
        })

        print('data:', data)

        if not data['anomalies']:
            return JsonResponse({"message": "No anomalies found for this video"})

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def delete_record_abnormal(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            save_path = data.get('file_path')
            # 查找并删除数据库记录
            file_record = AbnormalClip.objects.filter(save_path=save_path).first()
            if file_record:
                file_record.delete()
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'Record not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


@csrf_exempt
def delete_file(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print('data:', data)
            save_path = data.get('file_path')
            print('save_path:', save_path)
            # 检查文件是否存在并删除
            if os.path.exists(save_path):
                os.remove(save_path)
                return JsonResponse({'success': True})
            else:
                print('没找到文件')
                return JsonResponse({'success': False, 'error': 'File not found'}, status=404)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=405)


dir = f"{settings.SOURCEVIDEOS_ROOT}"
dir_sour = f"{settings.MEDIA_ROOT}/anomaly_mp4"
dir_res = f"{settings.MEDIA_ROOT}/result.mp4"
dir_at = f"{settings.MEDIA_ROOT}/anomaly_txt"
dir_xt = f"{settings.MEDIA_ROOT}/final_txt"
extension = "mp4"


def uploader(request):
    # 处理POST请求，即用户提交表单的情况
    if request.method == 'POST':
        # 创建 UploadUnitform 实例，包含请求的数据和文件
        form = UploadUnitform(request.POST, request.FILES)
        # 验证表单数据是否有效
        if form.is_valid():
            # 从请求中获取视频文件
            video_file = request.FILES['source_path']
            # 获取表单中提交的视频标题
            video_title = form.cleaned_data['source_title']
            # 获取视频文件的扩展名
            video_extension = os.path.splitext(video_file.name)[1]
            # 以 source_title 和原扩展名重新命名文件
            new_video_name = f"{video_title}{video_extension}"
            # 构建视频文件的临时保存路径
            video_path = os.path.join(dir, '', new_video_name)

            # 打开目标文件，准备写入
            with open(video_path, 'wb+') as destination:
                # 分块读取并写入视频文件，以处理大文件
                for chunk in video_file.chunks():
                    destination.write(chunk)

            # 使用 VideoFileClip 库获取视频时长
            video_clip = VideoFileClip(video_path)
            video_duration = int(video_clip.duration)
            video_clip.close()

            instance = form.save(commit=False)
            instance.upload_time = datetime.now()
            instance.video_duration = video_duration
            instance.title = video_title
            instance.save_path = video_path

            instance.end_time = instance.start_time + timedelta(seconds=video_duration)
            instance.monitor_id = 1
            # 保存实例到数据库
            instance.save()

            # 重定向到 'mainshow' 页面
            return redirect('mainshow')
        else:
            # 表单验证失败，抛出404错误
            raise Http404("Wrongtype.")
    else:
        # 处理GET请求，即用户请求上传表单的情况
        form = UploadUnitform()
        # 渲染上传表单页面
        return render(request, 'webuicore/uploader.html', {'form': form})


@csrf_exempt
def exe_vad(request):
    if request.method == 'POST':
        try:
            print('Received POST request', request)
            print('1\n')
            data = json.loads(request.body.decode('utf-8'))
            video_src = data.get('video_url')
            print('video_src:', video_src)
            if not video_src:
                return JsonResponse({'error': 'video_src is required'}, status=400)
            # 正则表达式模式，匹配 http(s)://.../media/
            pattern = r'^https?://[^/]+/media/'
            print('2\n')
            # 使用正则表达式进行替换
            print(local_prefix)
            video_src = re.sub(pattern, local_prefix, video_src)
            video_src = video_src.replace('/', '\\')
            print('video_src after regex:', video_src)
            # 查询数据库并打印结果
            source_videos = SourceVideo.objects.filter(save_path=video_src)
            print('source_videos:', source_videos[0].save_path if source_videos.exists() else 'No matching records found')
            if not source_videos.exists():
                return JsonResponse({'error': 'No matching record found'}, status=404)

            # 假设我们取第一个匹配的记录
            source_video_id = source_videos.first().source_id
            print('source_video_id:', source_video_id)
            result = det_anom(video_src, source_video_id=source_video_id)

            return JsonResponse(result, safe=False)
        except json.JSONDecodeError as e:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'Internal server error'}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


# 查询函数
def abnormal_clips_by_label(request, label):
    try:
        abnormal_clips = AbnormalClip.objects.filter(label=label)
        print("label: ", label)
        result = [
            {
                'abnormal_id': clip.abnormal_id,
                'source_id': clip.source_id,
                'save_path': clip.save_path.url,
                'title': clip.title,
                'label': clip.label,
                'caption': clip.caption,
                'score': clip.score,
                'start_time': clip.start_time.isoformat(),
                'end_time': clip.end_time.isoformat(),
            }
            for clip in abnormal_clips
        ]
        print("result: ", result)
        return JsonResponse(result, safe=False)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@csrf_exempt
def generate_video_caption(request):
    try:
        if request.method != 'POST':
            return JsonResponse({'success': False, 'error': 'Only POST requests are allowed'}, status=405)
        # 解析 POST 请求体
        data = json.loads(request.body.decode('utf-8'))
        video_path = data.get('video_url')  # 从请求中获取视频路径
        print('video_url:', video_path)
        # 正则表达式模式，匹配 http(s)://.../media/
        pattern = r'^https?://[^/]+/media/'

        # 使用正则表达式进行替换
        video_path = re.sub(pattern, 'media/', video_path)
        print("video_path after regex:", video_path)
        if not video_path or not os.path.exists(video_path):
            return JsonResponse({'success': False, 'error': 'Invalid video path'}, status=400)
        print("10\n") 
        frame_list = extract_frames(video_path)
        print("11\n")
        if not frame_list:
            return JsonResponse({'success': False, 'error': 'No frames extracted from the video'}, status=400)
        # 编码图像
        base64_image = encode_image(frame_list)
        client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx"
            api_key='sk-d7da78b936be4f1aabc1e2b5c52dd709',  # 替换为你的API密钥
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
        )
        completion = client.chat.completions.create(
            model="qwen-vl-max-latest",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            # 需要注意，传入BASE64，图像格式（即image/{format}）需要与支持的图片列表中的Content Type保持一致。"f"是字符串格式化的方法。
                            # PNG图像：  f"data:image/png;base64,{base64_image}"
                            # JPEG图像： f"data:image/jpeg;base64,{base64_image}"
                            # WEBP图像： f"data:image/webp;base64,{base64_image}"
                            "image_url": {"url": f"data:image/jpg;base64,{base64_image}"},
                        },
                        {"type": "text", "text": "这是一张包含异常情况的图片，请用一句话描述其异常情况"},
                    ],
                }
            ],
        )
        caption = completion.choices[0].message.content
        print("异常描述：", caption)
        video_path = video_path.replace('\\', '/')
        print("video_path", video_path)
        try:
            abnormal_clip = AbnormalClip.objects.filter(save_path=video_path).first()
            print(f"AbnormalClip found: {abnormal_clip}")

            abnormal_clip.caption = caption
            abnormal_clip.save()
            print(f"Caption updated successfully for save_path: {video_path}, new caption: {abnormal_clip.caption}")

            return JsonResponse({'success': True, 'caption': caption}, status=200)
        except AbnormalClip.DoesNotExist:
            print(f"AbnormalClip not found for save_path: {video_path}")
            return JsonResponse({'success': False, 'error': 'AbnormalClip record not found'}, status=404)
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
        return JsonResponse({'success': True, 'caption': caption}, status=200)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def extract_frames(video_path):
    # 获取视频文件名（不带扩展名）
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    # 创建以视频文件名为名称的文件夹
    output_folder = os.path.join(rf'{settings.MEDIA_ROOT}\temp', video_name)
    os.makedirs(output_folder, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    frame_path = None

    if cap.isOpened():
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames > 0:
            # 随机选择一帧
            random_frame_index = random.randint(0, total_frames - 1)
            cap.set(cv2.CAP_PROP_POS_FRAMES, random_frame_index)
            success, frame = cap.read()
            if success:
                # 构建帧文件名
                frame_filename = f"frame_{random_frame_index:04d}.jpg"
                frame_path = os.path.join(output_folder, frame_filename)

                # 保存帧到文件
                cv2.imwrite(frame_path, frame)

    cap.release()
    return frame_path


def abnormal_clips_by_score(request, threshold):
    try:
        threshold = float(threshold)
        print("threshold: ", threshold)
        abnormal_clips = AbnormalClip.objects.filter(score__gt=threshold)
        result = [
            {
                'abnormal_id': clip.abnormal_id,
                'source_id': clip.source_id,
                'save_path': clip.save_path.url,
                'title': clip.title,
                'label': clip.label,
                'caption': clip.caption,
                'score': clip.score,
                'start_time': clip.start_time.isoformat(),
                'end_time': clip.end_time.isoformat(),
            }
            for clip in abnormal_clips
        ]
        return JsonResponse(result, safe=False)
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Invalid threshold value'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


def popup_page(request):
    # 从 GET 请求中获取 videoUrl 参数
    video_url = request.GET.get('videoUrl')
    if not video_url:
        return JsonResponse({'success': False, 'error': 'videoUrl 参数未提供'}, status=400)

    # 正则表达式模式，匹配 http(s)://.../media/
    pattern = r'^https?://[^/]+/media/'

    # 使用正则表达式进行替换
    video_src = re.sub(pattern, local_prefix, video_url)
    video_src = video_src.replace('/', '\\')

    print('video_src', video_src)

    # 将 video_url 传递给模板
    context = {
        'video_src': video_src,
    }
    return render(request, 'mainshow/popup-page.html', context)


@csrf_exempt
def modify(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            label = data.get('label')
            score = data.get('score')
            caption = data.get('caption')
            video_src = data.get('video_src')
            video_src = video_src.replace('\\', '/')

            print('label: ', label)
            print('score: ', score)
            print('caption: ', caption)
            print('video_src: ', video_src)

            # 查找记录
            clip = AbnormalClip.objects.filter(save_path=video_src).first()

            # 更新记录
            clip.label = label
            clip.score = score
            clip.caption = caption

            # 保存更改
            clip.save()

            # 打印保存成功信息
            print(f"Record with video_src '{video_src}' updated successfully.")

            # 在这里处理数据，例如保存到数据库
            # 例如：
            # YourModel.objects.create(label=label, score=score, caption=caption, video_src=video_src)

            # 返回成功响应
            return JsonResponse({'status': 'success', 'message': 'Data saved successfully'})
        except Exception as e:
            # 返回错误响应
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
def gistest(request):
    
    import folium
    
    center_location=[34.032047,108.760922]
    # 创建地图对象，设置初始缩放级别
    m = folium.Map(
        location=center_location,
        zoom_start=16,  # 数字越大，缩放级别越高
        tiles="OpenStreetMap"  # 指定底图类型
    )
    monitors = Monitor.objects.filter()
    if monitors:
        
        for monitor in monitors:
            # 添加标记（Marker）到地图
            location = [monitor.location_lati,monitor.location_longi]
            sVidLists=SourceVideo.objects.filter(monitor_id=monitor.monitor_id).values_list('source_id', flat=True)
            for sVid in sVidLists:
                aClips=AbnormalClip.objects.filter(source_id=sVid)
                if aClips:
                    folium.Marker(
                        location=location,
                        popup=monitor.location_name,
                        tooltip=f"{monitor.location_name}出现异常，首个异常片段时间为{aClips.first().start_time} - {aClips.first().end_time}",
                        icon=folium.Icon(color="red", icon="info-sign")
                    ).add_to(m)
                    # 添加圆形区域（例如：以中心点为圆心，半径 2 公里的范围）
                    folium.Circle(
                        location=location,
                        radius=30,  # 单位：米
                        color="blue",
                        fill=True,
                        fill_color="lightred",
                        fill_opacity=0.5,
                        popup="30米半径区域"
                    ).add_to(m)
                    break;
                
            else:
                folium.Marker(
                    location=location,
                    popup=monitor.location_name,
                    tooltip=f"{monitor.location_name}正常",
                    icon=folium.Icon(color="blue", icon="info-sign")
                ).add_to(m)
                # 添加圆形区域（例如：以中心点为圆心，半径 2 公里的范围）
                folium.Circle(
                    location=location,
                    radius=30,  # 单位：米
                    color="green",
                    fill=True,
                    fill_color="lightgreen",
                    fill_opacity=0.5,
                    popup="30米半径区域"
                ).add_to(m)



    # 保存地图为 HTML 文件
    m.save("D:/COMPLEXPROJECTS/webui4VadCLIP_SE/templates/mainshow/gis_nwpu.html")

    print("地图已保存为 gis_nwpu.html，请用浏览器打开查看")
    return render(request, 'mainshow/gis_nwpu.html', {})