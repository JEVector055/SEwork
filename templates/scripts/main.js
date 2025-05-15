// 当文档内容加载完成后，执行指定函数
document.addEventListener('DOMContentLoaded', function () {
    // 本地 HTTP 服务器地址
    var filePath = document.getElementById('video-url').value;
    console.log('filePath:', filePath);
    const serverPath = 'http://localhost:8000';

    // 将 Windows 路径转换为相对路径（去除磁盘前缀，并替换反斜杠为正斜杠）
    const videoRelativePath = filePath
        .replace(/^.*media/, 'media')  // 提取相对路径
        .replace(/\\/g, '/');  // 替换反斜杠为正斜杠

    // 拼接完整的 HTTP URL
    const videoUrl = `${serverPath}/${videoRelativePath}`;
    // 设置视频源
    var videoPlayer = document.getElementById('source-video');
    var videoSource = document.getElementById('video-source');
    videoSource.src = videoUrl;

    // 重新加载并播放视频
    videoPlayer.load();  // 重新加载视频
    videoPlayer.play();  // 播放视频

    // 示例：打印 file_path 到控制台
    console.log('Video file path:', filePath);

    // 发送GET请求获取文件列表
    fetch('/get-files-detail')
        .then(response => response.json())
        .then(filesData => {
            // 获取文件列表元素
            const fileList = document.getElementById('file-list');
            // 遍历文件数据，创建并添加文件链接到文件列表
            filesData.forEach(file => {
                const li = document.createElement('li');
                const a = document.createElement('a');
                a.href = '#';

                // 提取文件名
                const fileName = file.split('/').pop();
                a.textContent = fileName;  // 显示文件名而不是完整路径

                // 为文件链接添加点击事件，用于播放视频
                a.onclick = function () {
                    const videoPlayer = document.getElementById('source-video');

                    // 本地 HTTP 服务器地址
                    const serverPath = 'http://localhost:8000';

                    // 将 Windows 路径转换为相对路径（去除磁盘前缀，并替换反斜杠为正斜杠）
                    const videoRelativePath = file
                        .replace(/^.*media/, 'media')  // 提取相对路径
                        .replace(/\\/g, '/');  // 替换反斜杠为正斜杠

                    // 拼接完整的 HTTP URL
                    const videoUrl = `${serverPath}/${videoRelativePath}`;

                    videoPlayer.src = videoUrl;  // 设置为 HTTP 路径
                    videoPlayer.load();  // 重新加载视频
                    videoPlayer.play();  // 播放视频
                };

                // 创建删除按钮
                const deleteBtn = document.createElement('button');
                deleteBtn.className = 'delete-btn'; // 添加类名以便应用CSS样式
                deleteBtn.innerHTML = '<i class="fa-solid fa-xmark"></i>'; // 使用图标
                deleteBtn.onclick = function () {
                    // 这里添加删除文件的逻辑
                    console.log('Delete file:', file);
                    // 通常需要发送一个请求到服务器来删除文件
                    // 例如: fetch('/delete-file', { method: 'POST', body: JSON.stringify({ filename: file }) })
                    // 然后从DOM中移除这个li元素
                    // li.remove();
                };

                li.appendChild(a);
                li.appendChild(deleteBtn);
                fileList.appendChild(li);
            });
        })
        .catch(error => {
            console.error('Error fetching files:', error);
        });
});

function playVideo(videoUrl) {
    const videoPlayer = document.getElementById('source-video');
    videoPlayer.src = videoUrl;  // 设置主视频播放器的源
    videoPlayer.load();           // 重新加载视频
    videoPlayer.play();           // 播放视频
}
