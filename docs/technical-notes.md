# 技術解説書

## MJPEGの仕組みと利点

MJPEGストリーミングは、Motion JPEG（JPEG画像のシーケンス）を使用して動画をストリーミングする技術です。

### 主な特徴
- 各フレームが独立したJPEG画像として送信される
- HTTP経由で簡単に実装可能
- ブラウザでネイティブサポートされている
- レイテンシーが低い

### 実装方法
```python
Content-Type: multipart/x-mixed-replace; boundary=frame
--frame
Content-Type: image/jpeg

[JPEG データ]
--frame
```

## フレーム処理の説明

カメラからのフレーム取得は以下のような流れで処理されます：

1. OpenCV（cv2）によるカメラキャプチャ
2. フレームの取得とJPEG変換
3. マルチパート形式でのストリーミング配信

### フレーム取得の最適化
- スレッドベースの非同期処理
- フレームバッファの適切な管理
- CPU使用率の制御（スリープ時間の調整）

## 並列処理の実装方法

本システムでは、以下の並列処理を実装しています：

1. カメラキャプチャスレッド
    - 継続的なフレーム取得
    - スレッドセーフなフレームバッファ管理
    - Lockによる排他制御

2. FastAPIのasyncioベース処理
    - 非同期I/Oによる効率的なHTTPハンドリング
    - ストリーミングレスポンスの非同期生成

### スレッド安全性の確保
```python
with self.lock:
    self.frame = frame  # スレッドセーフなフレーム更新
```

## 将来の拡張可能性

### 画像処理機能の追加
- 物体検出
- 動体検知
- 画像フィルタリング

### システム拡張
- マルチカメラ対応
- 録画機能
- 画像認識AIの統合
- リアルタイム解析機能

### パフォーマンス最適化
- フレームレートの動的調整
- 画質の自動調整
- 負荷分散処理

## キャプチャ機能の実装

### 基本設計
- スペースキーイベントのキャプチャと処理
- フレームバッファからの画像取得
- タイムスタンプ生成による一意なファイル名作成
- 非同期での画像保存処理

### 実装の詳細
```python
# フレームキャプチャ処理
async def capture_frame():
    with frame_lock:
        frame = current_frame.copy()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"capture_{timestamp}.jpg"
    
    # 非同期でファイル保存
    await asyncio.to_thread(cv2.imwrite,
        f"captures/{filename}", frame)
```

### イベント処理の流れ
1. クライアントからのキーイベント受信（WebSocket）
2. サーバーサイドでのフレーム取得
3. タイムスタンプ生成とファイル名作成
4. 非同期での画像保存処理
5. クライアントへの保存完了通知

### 最適化ポイント
- フレームバッファのスレッドセーフな処理
- 非同期I/Oによる効率的なファイル保存
- メモリ使用量の最適化（フレームのディープコピー）

## フロントエンド実装（TypeScript）

### 開発環境
- TypeScript + Webpack構成
- 型安全性の確保
- モジュール化されたコード構造

### コードの構成
- src/static/scripts/camera.ts: カメラ制御
- src/static/scripts/main.ts: メインの処理
- webpack.config.js: ビルド設定

### ビルドプロセス
1. TypeScriptコードのコンパイル
2. Webpackでのバンドル
3. 最適化された単一JSファイルの生成

## マルチカメラサポート

### 1. Docker環境でのカメラ管理
- Dockerコンテナでのデバイスアクセス
  ```yaml
  devices:
    - "/dev:/dev"  # すべてのデバイスにアクセス可能
  privileged: true  # デバイスアクセスの権限付与
  group_add:
    - video  # videoグループに追加
  ```
- v4l2-utilsを使用したデバイス管理
  ```bash
  v4l2-ctl --list-devices  # デバイス一覧の取得
  ```

### 2. カメラデバイスの検出と管理
- バックエンドでの実装（Python/FastAPI）
  ```python
  @app.get("/api/cameras")
  async def list_cameras():
      # v4l2-ctlコマンドの実行と結果パース
      devices = Camera.list_available_devices()
      return {"devices": devices}
  ```

### 3. フロントエンド実装（TypeScript）
- インターフェース定義
  ```typescript
  interface CameraDevice {
      name: string;
      path: string;
  }
  ```

- カメラ選択UI
  - プルダウンメニューでのデバイス選択
  - 動的なストリーム切り替え
  - エラー状態の表示

### 4. カメラ切り替えの仕組み
1. UIでカメラを選択
2. バックエンドAPIにリクエスト送信
3. カメラデバイスの切り替え
4. ストリーミングの再初期化

### 5. エラーハンドリング
- デバイスアクセスエラー
- ストリーム切り替えエラー
- UIでのエラー表示

### 6. 設計上の考慮点
- スレッドセーフなカメラ制御
- リソースの適切な解放
- 非同期処理による応答性の確保