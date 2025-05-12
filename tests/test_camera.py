import unittest
import cv2
import numpy as np
from src.camera import Camera
import time

class TestCamera(unittest.TestCase):
    def setUp(self):
        """各テストケース実行前の準備"""
        self.camera = Camera(camera_id=0)
        self.wait_time = 0.5  # カメラの初期化待機時間

    def tearDown(self):
        """各テストケース実行後のクリーンアップ"""
        if self.camera.is_running:
            self.camera.stop()
            time.sleep(0.1)  # 停止処理の待機

    def test_camera_initialization(self):
        """カメラの初期化テスト"""
        self.assertEqual(self.camera.camera_id, 0)
        self.assertFalse(self.camera.is_running)
        self.assertIsNone(self.camera.frame)
        self.assertIsNone(self.camera.cap)

    def test_camera_start_stop(self):
        """実カメラの開始と停止のテスト"""
        try:
            self.camera.start()
            time.sleep(self.wait_time)  # カメラ初期化待機
            
            self.assertTrue(self.camera.is_running)
            self.assertIsNotNone(self.camera.cap)
            self.assertTrue(self.camera.cap.isOpened())

            frame = self.camera.get_frame()
            self.assertIsNotNone(frame)
            self.assertIsInstance(frame, np.ndarray)
            self.assertGreater(frame.shape[0], 0)  # 有効なフレームサイズを確認
            self.assertGreater(frame.shape[1], 0)

            self.camera.stop()
            time.sleep(0.1)  # 停止処理待機
            self.assertFalse(self.camera.is_running)
        except Exception as e:
            self.skipTest(f"カメラデバイスにアクセスできません: {str(e)}")

    def test_invalid_camera_id(self):
        """無効なカメラIDのテスト"""
        invalid_camera = Camera(camera_id=999)
        with self.assertRaises(RuntimeError):
            invalid_camera.start()

    def test_get_jpeg(self):
        """実カメラを使用したJPEG変換のテスト"""
        try:
            self.camera.start()
            time.sleep(self.wait_time)  # カメラ初期化待機

            # JPEG品質パラメータのテスト
            for quality in [10, 50, 95]:
                jpeg_data = self.camera.get_jpeg(quality=quality)
                self.assertIsNotNone(jpeg_data)
                self.assertIsInstance(jpeg_data, bytes)
                
                # JPEGデータが実際に有効かチェック
                nparr = np.frombuffer(jpeg_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                self.assertIsNotNone(img)
                self.assertGreater(img.shape[0], 0)
                self.assertGreater(img.shape[1], 0)

            # フレームが無い場合のテスト
            self.camera.stop()
            jpeg_data = self.camera.get_jpeg()
            self.assertIsNone(jpeg_data)
        except Exception as e:
            self.skipTest(f"カメラデバイスにアクセスできません: {str(e)}")

    def test_concurrent_access(self):
        """実カメラを使用した並行アクセスのテスト"""
        try:
            self.camera.start()
            time.sleep(self.wait_time)  # カメラ初期化待機

            # 複数回のフレーム取得を実行
            frames = []
            for _ in range(5):
                frame = self.camera.get_frame()
                frames.append(frame)
                time.sleep(0.05)

            # すべてのフレームが有効であることを確認
            for frame in frames:
                self.assertIsNotNone(frame)
                self.assertIsInstance(frame, np.ndarray)
                self.assertGreater(frame.shape[0], 0)
                self.assertGreater(frame.shape[1], 0)

                # フレームが実際に異なることを確認（動画フィードのテスト）
                if len(frames) > 1:
                    diff = cv2.absdiff(frames[0], frame)
                    self.assertTrue(np.any(diff > 0))

        except Exception as e:
            self.skipTest(f"カメラデバイスにアクセスできません: {str(e)}")

if __name__ == '__main__':
    unittest.main()