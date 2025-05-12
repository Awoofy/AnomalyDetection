from fastapi.testclient import TestClient
import unittest
from src.main import app, camera
import time
import cv2
import numpy as np

class TestBasicAPI(unittest.TestCase):
    """基本的なAPIエンドポイントのテスト"""
    def setUp(self):
        self.client = TestClient(app)
        try:
            # カメラが正しく初期化されるまで待機
            if not camera.is_running:
                camera.start()
                time.sleep(0.5)
        except Exception as e:
            # カメラ初期化エラーは無視してテストを続行
            print(f"Warning: カメラの初期化をスキップ: {str(e)}")

    def tearDown(self):
        """各テストケース実行後のクリーンアップ"""
        if camera.is_running:
            camera.stop()
            time.sleep(0.1)

    def test_root_endpoint(self):
        """ルートエンドポイントのテスト"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertIn('meta http-equiv="refresh"', response.text)

    def test_static_files(self):
        """静的ファイルの提供テスト"""
        response = self.client.get("/static/index.html")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])

    def test_invalid_endpoint(self):
        """無効なエンドポイントのテスト"""
        response = self.client.get("/invalid")
        self.assertEqual(response.status_code, 404)

    def test_video_feed(self):
        """ビデオフィードエンドポイントのテスト"""
        if not camera.is_running:
            self.skipTest("カメラが利用できないためスキップします")
            
        # ビデオフィードのレスポンスを取得
        response = self.client.get("/video_feed")
        
        # レスポンスのヘッダーを確認
        self.assertEqual(response.status_code, 200)
        self.assertIn("multipart/x-mixed-replace", response.headers["content-type"])

if __name__ == '__main__':
    unittest.main()