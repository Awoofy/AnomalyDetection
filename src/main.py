from fastapi import FastAPI, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
import asyncio
from .camera import Camera

app = FastAPI()

# 静的ファイルのマウント
app.mount("/static", StaticFiles(directory="src/static"), name="static")

# カメラインスタンスの初期化（環境変数からカメラIDを取得）
import os
camera_id = int(os.getenv('CAMERA_ID', '1'))  # デフォルトでvideo1を使用
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)