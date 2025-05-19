import cv2
import numpy as np
from threading import Thread, Lock
import time
import re
import subprocess
import logging
from typing import List, Dict

# ロガーの設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Camera:
    # ロガーの設定
    logger = logging.getLogger(__name__)
    
    # Device Capsのパターン（スペースを柔軟に処理）
    VIDEO_CAPS_PATTERN = re.compile(r'Device\s+Caps\s*:\s*0x04200001')
    @staticmethod
    def list_available_devices() -> List[Dict[str, str]]:
        """ビデオキャプチャ可能なカメラデバイスの一覧を取得"""
        try:
            # デバイス一覧の取得
            result = subprocess.run(
                ['v4l2-ctl', '--list-devices'],
                capture_output=True,
                text=True,
                check=True
            )

            devices = []
            current_device = None

            for line in result.stdout.split('\n'):
                if ':' in line and 'dev' not in line:
                    # 新しいデバイスの開始
                    current_device = line.split(':')[0].strip()
                elif '/dev/video' in line:
                    device_path = line.strip()
                    # Device Capsの確認
                    caps_result = subprocess.run(
                        ['v4l2-ctl', '-d', device_path, '-D'],
                        capture_output=True,
                        text=True
                    )
                    
                    if (caps_result.returncode == 0 and
                        Camera.VIDEO_CAPS_PATTERN.search(caps_result.stdout)):
                        # ビデオキャプチャ可能なデバイスのみ追加
                        devices.append({
                            'name': f"{current_device} ({device_path})",
                            'path': device_path
                        })

            return devices
        except subprocess.CalledProcessError as e:
            Camera.logger.error(f"デバイス一覧の取得に失敗: {e}")
            return []
        except Exception as e:
            Camera.logger.error(f"予期せぬエラーが発生: {e}")
            return []

    def __init__(self, device_path: str = "/dev/video0"):
        """カメラクラスの初期化"""
        self.camera_id = device_path
        self.is_running = False
        self.lock = Lock()
        self.frame = None
        self.cap = None
        self.thread = None

    def start(self):
        """カメラのキャプチャを開始"""
        if self.is_running:
            return

        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                raise RuntimeError(f"カメラID {self.camera_id} を開けません")
            
            self.is_running = True
            self.thread = Thread(target=self._capture_loop, daemon=True)
            self.thread.start()
        except Exception as e:
            if self.cap:
                self.cap.release()
                self.cap = None
            raise RuntimeError(f"カメラの初期化に失敗しました: {str(e)}")

    def stop(self):
        """カメラのキャプチャを停止"""
        self.is_running = False
        if self.thread:
            self.thread.join()
        if self.cap:
            self.cap.release()

    def _capture_loop(self):
        """カメラからフレームを継続的に取得"""
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            with self.lock:
                self.frame = frame
            time.sleep(0.01)  # CPU使用率を抑制

    def get_frame(self):
        """現在のフレームを取得"""
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()

    def get_jpeg(self, quality=95):
        """現在のフレームをJPEG形式で取得"""
        frame = self.get_frame()
        if frame is None:
            return None
        
        ret, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
        if not ret:
            return None
            
        return jpeg.tobytes()

    def capture_image(self, save_path):
        """
        現在のフレームを画像として保存
        Args:
            save_path (str): 保存するファイルパス
        Returns:
            bool: 保存に成功したらTrue、失敗したらFalse
        """
        frame = self.get_frame()
        if frame is None:
            return False
            
        try:
            # 画像を保存
            return cv2.imwrite(save_path, frame)
        except Exception as e:
            Camera.logger.error(f"画像の保存に失敗: {str(e)}")
            return False

    def __del__(self):
        """デストラクタ: リソースの解放"""
        self.stop()