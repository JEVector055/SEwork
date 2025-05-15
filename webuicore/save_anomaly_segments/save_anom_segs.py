import os
from datetime import timedelta

import cv2
import torch
from PIL import Image
from django.utils import timezone
from torch import nn
from tqdm import tqdm

from . import clip
from . import vadclip
from ..models import SourceVideo, AbnormalClip

# import hyperparams
# args = hyperparams.parser.parse_args()

classes_num = 14
embed_dim = 512
visual_length = 256
visual_width = 512
visual_head = 1
visual_layers = 2
attn_window = 8
prompt_prefix = 10
prompt_postfix = 10
device = 'cuda' if torch.cuda.is_available() else 'cpu'
vadclip_path = 'webuicore/save_anomaly_segments/vadclip/model_ucf.pth'

clip_model, clip_preprocess = clip.load("ViT-B/16", device)
vadclip_model = vadclip.CLIPVAD(
    classes_num, embed_dim, visual_length, visual_width,
    visual_head, visual_layers, attn_window,
    prompt_prefix, prompt_postfix, device
)
vadclip_param = torch.load(vadclip_path, weights_only=True)
vadclip_model.load_state_dict(vadclip_param)

label_map = {
    'Normal': 'Normal', 'Abuse': 'Abuse', 'Arrest': 'Arrest', 'Arson': 'Arson', 'Assault': 'Assault',
    'Burglary': 'Burglary', 'Explosion': 'Explosion', 'Fighting': 'Fighting',
    'RoadAccidents': 'RoadAccidents', 'Robbery': 'Robbery', 'Shooting': 'Shooting',
    'Shoplifting': 'Shoplifting', 'Stealing': 'Stealing', 'Vandalism': 'Vandalism'
}
prompt_text = vadclip.get_prompt_text(label_map)


def det_anom(video_src, source_video_id=1):
    cap = cv2.VideoCapture(video_src)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    print(f"Total Frames: {frame_count}, FPS: {fps}")
    progress_bar = tqdm(total=frame_count, desc="Processing Frames", unit="frame")

    video_frame_list = []
    video_features_list = []
    anomaly_frames = []
    anomaly_start_frame = None
    anomaly_seg_paths = []
    labels_list = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        video_frame_list.append(frame)
        with torch.no_grad():
            frame_pil = Image.fromarray(frame)
            frame_preprocessed = clip_preprocess(frame_pil).unsqueeze(0).to(device)
            frame_features = clip_model.encode_image(frame_preprocessed)

            video_features_list.append(frame_features)

            if len(video_features_list) >= visual_length:
                video_features = torch.cat(video_features_list, dim=0)
                video_features = video_features.reshape(1, 256, 512)
                lengths = torch.tensor([visual_length]).to(device)
                scores = eval_anomaly_scores(vadclip_model, video_features, lengths, device)

                # Min-Max 归一化
                min_score = scores.min()
                max_score = scores.max()
                normalized_scores = (scores - min_score) / (max_score - min_score)

                scores = normalized_scores
                # print(scores)
                for j, text_score in enumerate(scores):
                    score_value = text_score.item()
                    if score_value >= 0.6:
                        if anomaly_start_frame is None:
                            anomaly_start_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - len(video_frame_list) + j
                        anomaly_frames.append(video_frame_list[j])
                    else:
                        if anomaly_frames and len(anomaly_frames) > 3:
                            print('异常帧列表长度:', len(anomaly_frames))
                            anomaly_end_frame = int(cap.get(cv2.CAP_PROP_POS_FRAMES)) - len(video_frame_list) + j
                            start_time = anomaly_start_frame / fps
                            end_time = anomaly_end_frame / fps
                            output_dir = f"G:/Code/video_management/webui4VadCLIP-develop/media/AnomalyVideo/anomaly_{start_time:.2f}_{end_time:.2f}.mp4"
                            anomaly_seg_paths.append(output_dir)
                            os.makedirs(os.path.dirname(output_dir), exist_ok=True)
                            save_frames_as_mp4(anomaly_frames, output_dir, fps)
                            try:
                                source_video = SourceVideo.objects.get(source_id=source_video_id)
                                original_start_time = source_video.start_time
                            except SourceVideo.DoesNotExist:
                                print(f"SourceVideo with id {source_video_id} does not exist.")
                                original_start_time = timezone.now()  # 如果找不到，默认使用当前时间

                            print('original_start_time:', original_start_time)
                            new_start_time = original_start_time + timedelta(seconds=start_time)
                            new_end_time = original_start_time + timedelta(seconds=end_time)
                            temp_scores = scores[j - 1].item()
                            # 获取异常片段的最后一帧的特征
                            last_frame = anomaly_frames[-1]
                            # 调用 generate_label 函数获取标签
                            label = generate_label(clip_model, clip_preprocess, last_frame, list(label_map.keys()))
                            print("label: ", label)
                            try:
                                # 保存异常片段信息到数据库
                                AbnormalClip.objects.create(
                                    source_id=source_video_id or 1,  # 使用传入的 source_video_id 或默认值
                                    save_path=output_dir,
                                    title=f"Anomaly_from {new_start_time}s",
                                    label=label,  # 根据实际情况设置标签
                                    caption='Detected anomaly segment',
                                    score=temp_scores,
                                    start_time=new_start_time,
                                    end_time=new_end_time
                                )
                            except Exception as e:
                                print(f"Error saving to database: {e}")

                            anomaly_frames = []
                            anomaly_start_frame = None

                video_frame_list = []
                video_features_list = []
                torch.cuda.empty_cache()

            progress_bar.update(1)

    if anomaly_frames:
        anomaly_end_frame = frame_count
        start_time = anomaly_start_frame / fps
        end_time = anomaly_end_frame / fps
        output_dir = f"data/anomaly_mp4/anomaly_{start_time:.2f}_{end_time:.2f}.mp4"
        anomaly_seg_paths.append(output_dir)
        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        save_frames_as_mp4(anomaly_frames, output_dir, fps)

    progress_bar.close()
    cap.release()
    return anomaly_seg_paths


def save_frames_as_mp4(frames, output_filename, fps=30):
    height, width, _ = frames[0].shape
    fourcc = cv2.VideoWriter_fourcc(*'H264')
    video = cv2.VideoWriter(output_filename, fourcc, fps, (width, height))

    for frame in frames:
        video.write(frame)

    video.release()


def generate_label(model, preprocess, frame, labels):
    frame_pil = Image.fromarray(frame)
    frame_preprocessed = preprocess(frame_pil).unsqueeze(0).to(device)
    with torch.no_grad():
        frame_features = model.encode_image(frame_preprocessed)
        label_tokens = clip.tokenize(labels).to(device)
        label_embeddings = model.token_embedding(label_tokens).type(model.dtype)
        label_features = model.encode_text(label_embeddings, label_tokens)
        similarities = (frame_features @ label_features.T).squeeze(0)
        best_match_index = similarities.argmax().item()
    return labels[best_match_index]


def eval_anomaly_scores(model, video_features, sequence_lengths, device):
    model.to(device)
    model.eval()
    sigmoid = nn.Sigmoid()
    with torch.no_grad():
        padding_mask = vadclip.get_batch_mask(sequence_lengths, visual_length).to(device)
        _, logits, _ = model(video_features, padding_mask, prompt_text, sequence_lengths)
        logits = logits.reshape(logits.shape[0] * logits.shape[1], logits.shape[2])
        scores = sigmoid(logits)
    return scores
