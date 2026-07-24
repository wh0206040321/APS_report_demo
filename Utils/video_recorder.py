import random
import threading
import time
import os
import re
from datetime import datetime
import cv2
import numpy as np
import mss
import subprocess


class VideoRecorder:
    def __init__(self):
        self.recording = False
        self.thread = None
        self.output_path = None
        self.video_writer = None
        self.fps = 10
        self.video_dir = os.path.abspath("report/videos")
        self.lock = threading.Lock()  # 添加线程锁，保证线程安全

    def _clear_old_videos(self):
        """清除旧的视频文件"""
        if os.path.exists(self.video_dir):
            for file in os.listdir(self.video_dir):
                file_path = os.path.join(self.video_dir, file)
                if os.path.isfile(file_path):
                    os.remove(file_path)

    def start(self, driver, test_name: str):
        """开始录制视频，确保文件名唯一"""
        if self.recording:
            return

        os.makedirs(self.video_dir, exist_ok=True)

        # 使用时间戳和随机数确保文件名唯一
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        clean_name = re.sub(r'[\\/*?:"<>|]', "_", test_name)

        # 为了确保唯一性，加入随机后缀
        random_suffix = str(random.randint(1000, 9999))  # 随机数部分
        self.output_path = os.path.join(self.video_dir, f"{clean_name}_{timestamp}_{random_suffix}.mp4")

        self.recording = True
        self.thread = threading.Thread(
            target=self._record,
            daemon=True
        )
        self.thread.start()
        print(f"🎥 录屏已启动: {self.output_path}")

    def _record(self):
        """
        录制循环 - MSS截图直接写入视频
        """

        max_duration = 120
        start_time = time.time()
        frame_interval = 1.0 / self.fps

        with mss.mss() as sct:

            monitor = sct.monitors[1]

            # 获取第一帧，确定尺寸
            screenshot = sct.grab(monitor)

            frame = np.array(screenshot)

            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGRA2BGR
            )

            height, width = frame.shape[:2]

            fourcc = cv2.VideoWriter_fourcc(
                *'avc1'
            )

            self.video_writer = cv2.VideoWriter(
                self.output_path,
                fourcc,
                self.fps,
                (width, height)
            )

            frame_count = 0

            while self.recording and (
                    time.time() - start_time
            ) < max_duration:

                try:

                    screenshot = sct.grab(monitor)

                    frame = np.array(
                        screenshot
                    )

                    frame = cv2.cvtColor(
                        frame,
                        cv2.COLOR_BGRA2BGR
                    )

                    # 直接写入视频
                    with self.lock:
                        self.video_writer.write(frame)

                    frame_count += 1

                    time.sleep(frame_interval)


                except Exception as e:
                    print(
                        f"录制异常: {e}"
                    )
                    break

            # 释放视频
            if self.video_writer:
                self.video_writer.release()
                self.video_writer = None

            file_size = (
                    os.path.getsize(self.output_path)
                    /
                    1024
                    /
                    1024
            )

            print(
                f"✅ 录屏完成: {self.output_path}"
            )

            print(
                f"   帧数:{frame_count}"
                f" 大小:{file_size:.2f}MB"
            )

            # 压缩
            self._compress_video()

    def stop(self):
        """停止录屏"""
        if not self.recording:
            return None

        self.recording = False

        # 等待录屏线程结束
        if hasattr(self, "thread") and self.thread.is_alive():
            self.thread.join()

        print(f"🛑 录屏已停止: {self.output_path}")

        # 返回视频路径
        return self.output_path

    def _compress_video(self):
        """
        使用 ffmpeg 压缩视频
        """

        if not os.path.exists(self.output_path):
            return

        compress_path = self.output_path.replace(
            ".mp4",
            "_compress.mp4"
        )

        ffmpeg_path = r"D:\ffmpeg-8.1.2-essentials_build\bin\ffmpeg.exe"

        command = [
            ffmpeg_path,
            "-i",
            self.output_path,

            # 视频编码
            "-c:v",
            "libx264",

            # 压缩比例
            "-crf",
            "28",

            # 编码速度
            "-preset",
            "fast",

            compress_path,

            "-y"
        ]

        try:
            subprocess.run(
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            if os.path.exists(compress_path):
                old_size = os.path.getsize(self.output_path) / 1024 / 1024
                new_size = os.path.getsize(compress_path) / 1024 / 1024

                print(
                    f"🎬 视频压缩完成: {old_size:.2f}MB → {new_size:.2f}MB"
                )

                # 删除原视频
                os.remove(self.output_path)

                # 新视频替换旧路径
                self.output_path = compress_path


        except Exception as e:
            print(f"❌ 视频压缩失败: {e}")


video_recorder = VideoRecorder()