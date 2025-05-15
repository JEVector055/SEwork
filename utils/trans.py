import os

import ffmpeg


def convert_to_h264_mp4(input_file, output_file):
    try:
        # 使用 FFmpeg 将视频转换为 H.264 编码的 MP4 文件
        (
            ffmpeg
            .input(input_file)
            .output(output_file, vcodec='libx264', acodec='aac', format='mp4')
            .run(overwrite_output=True)
        )
        print(f"转换成功：{input_file} -> {output_file}")
    except ffmpeg.Error as e:
        print(f"转换失败：{input_file} - {e.stderr.decode()}")


def main():
    # 获取当前目录下的所有文件
    current_directory = os.getcwd()
    files = os.listdir(current_directory)

    # 过滤出视频文件（假设扩展名为 .mp4, .avi, .mov, .mkv）
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
    video_files = [f for f in files if os.path.splitext(f)[1].lower() in video_extensions]

    # 转换每个视频文件
    for video_file in video_files:
        input_file = os.path.join(current_directory, video_file)
        output_file = os.path.join(current_directory, video_file)  # 覆盖原文件
        convert_to_h264_mp4(input_file, output_file)


if __name__ == "__main__":
    main()
