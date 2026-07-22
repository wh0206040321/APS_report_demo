import random
import threading
import time
import os
import re
from datetime import datetime
import cv2
import numpy as np
import mss


class VideoRecorder:
    def __init__(self):
        self.recording = False
        self.thread = None
        self.output_path = None
        self.frames = []
        self.fps = 10  # 10帧/秒，足够看清操作过程
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
        self.frames = []
        self.thread = threading.Thread(target=self._record, daemon=True)
        self.thread.start()
        print(f"🎥 录屏已启动: {self.output_path}")

    def _record(self):
        """录制循环 - 使用 MSS 高性能截图"""
        max_duration = 120  # 最多录制120秒
        start_time = time.time()
        frame_interval = 1.0 / self.fps

        with mss.mss() as sct:
            # 获取主显示器
            monitor = sct.monitors[1]

            while self.recording and (time.time() - start_time) < max_duration:
                try:
                    # MSS 截图（比 PyAutoGUI 快 10 倍）
                    screenshot = sct.grab(monitor)
                    # 转换为 OpenCV 格式
                    frame = np.array(screenshot)
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

                    # 使用线程锁保证线程安全
                    with self.lock:
                        self.frames.append(frame)

                    time.sleep(frame_interval)
                except Exception as e:
                    print(f"录制异常: {e}")
                    break

        if len(self.frames) >= 5:
            self._save_as_mp4()
        else:
            print(f"⚠️ 帧数不足 ({len(self.frames)} 帧)，放弃保存")

    def _save_as_mp4(self):
        """将帧序列保存为 MP4"""
        try:
            height, width = self.frames[0].shape[:2]

            fourcc = cv2.VideoWriter_fourcc(*'avc1')
            video_writer = cv2.VideoWriter(self.output_path, fourcc, self.fps, (width, height))

            # 写入视频时使用线程锁，确保没有并发问题
            with self.lock:
                for frame in self.frames:
                    video_writer.write(frame)

            video_writer.release()

            file_size = os.path.getsize(self.output_path) / (1024 * 1024)
            print(f"✅ 录屏已保存: {self.output_path}")
            print(f"   帧数: {len(self.frames)}, 时长: {len(self.frames) / self.fps:.1f}秒, 大小: {file_size:.2f}MB")

        except Exception as e:
            print(f"❌ 保存失败: {e}")

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


video_recorder = VideoRecorder()