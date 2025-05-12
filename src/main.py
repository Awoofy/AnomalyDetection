from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, JSONResponse
import asyncio
from datetime import datetime
import os
from pathlib import Path
from .camera import Camera

app = FastAPI()

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# カメラインスタンスの初期化（環境変数からカメラIDを取得）
# 環境変数の設定
camera_id = int(os.getenv('CAMERA_ID', '1'))  # デフォルトでvideo1を使用
CAPTURE_DIR = os.getenv('CAPTURE_DIR', 'captures')  # キャプチャ画像の保存ディレクトリ

# キャプチャディレクトリの作成
Path(CAPTURE_DIR).mkdir(parents=True, exist_ok=True)

camera = Camera(camera_id=camera_id)

@app.on_event("startup")
async def startup_event():
    """アプリケーション起動時にカメラを開始"""
    camera.start()

@app.on_event("shutdown")
async def shutdown_event():
    """アプリケーション終了時にカメラを停止"""
    camera.stop()

async def mjpeg_generator():
    """MJPEGストリームのジェネレータ関数"""
    while True:
        jpeg = camera.get_jpeg()
        if jpeg is not None:
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + jpeg + b'\r\n'
        await asyncio.sleep(0.1)  # フレームレートの制御

@app.get("/")
async def root():
    """ルートページにリダイレクト"""
    return Response(
        '<meta http-equiv="refresh" content="0; url=/static/index.html">',
        media_type="text/html"
    )

@app.get("/video_feed")
async def video_feed():
    """MJPEGストリームのエンドポイント"""
    return StreamingResponse(
        mjpeg_generator(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.post("/capture")
async def capture():
    """
    現在のフレームをキャプチャして保存
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{timestamp}.jpg"
    save_path = str(Path(CAPTURE_DIR) / filename)
    
    if camera.capture_image(save_path):
        return JSONResponse({
            "status": "success",
            "message": "画像を保存しました",
            "filename": filename
        })
    else:
        return JSONResponse({
            "status": "error",
            "message": "画像の保存に失敗しました"
        }, status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)