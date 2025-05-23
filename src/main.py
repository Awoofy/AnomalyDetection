from fastapi import FastAPI, Response, HTTPException
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
camera_device = os.getenv('CAMERA_DEVICE', '/dev/video0')  # デフォルトでvideo0を使用
CAPTURE_DIR = os.getenv('CAPTURE_DIR', 'captures')  # キャプチャ画像の保存ディレクトリ

# キャプチャディレクトリの作成
Path(CAPTURE_DIR).mkdir(parents=True, exist_ok=True)

camera = Camera(device_path=camera_device)

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

@app.get("/api/cameras")
async def list_cameras():
    """利用可能なカメラの一覧を返す"""
    try:
        devices = Camera.list_available_devices()
        return {"devices": devices}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from pydantic import BaseModel

class CameraSelectRequest(BaseModel):
    device_path: str

@app.post("/api/camera/select")
async def select_camera(request: CameraSelectRequest):
    """カメラデバイスを切り替える"""
    try:
        device_path = request.device_path
        
        # 利用可能なデバイスの確認
        available_devices = [dev["path"] for dev in Camera.list_available_devices()]
        if device_path not in available_devices:
            raise HTTPException(status_code=400, detail="指定されたカメラデバイスは利用できません")

        # 現在のカメラを停止
        camera.stop()
        
        try:
            # 新しいデバイスでカメラを再初期化
            camera.camera_id = device_path
            camera.start()
        except Exception as e:
            # 新しいカメラの初期化に失敗した場合は元のカメラに戻す
            camera.camera_id = camera_device
            camera.start()
            raise HTTPException(status_code=500, detail=f"カメラの切り替えに失敗しました: {str(e)}")
        
        return {"status": "success", "message": f"カメラを{device_path}に切り替えました"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"予期せぬエラーが発生しました: {str(e)}")

# 解像度設定用のモデル
class ResolutionRequest(BaseModel):
    width: int
    height: int

@app.get("/api/camera/resolutions")
async def get_resolutions():
    """カメラがサポートする解像度一覧を取得"""
    try:
        resolutions = camera.get_supported_resolutions()
        return {"resolutions": resolutions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/camera/resolution")
async def set_resolution(request: ResolutionRequest):
    """カメラの解像度を設定"""
    try:
        if camera.set_resolution(request.width, request.height):
            return {"message": f"解像度を{request.width}x{request.height}に設定しました"}
        raise HTTPException(status_code=500, detail="解像度の設定に失敗しました")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)