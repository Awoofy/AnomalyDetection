# AnomalyDetection

画像認識AIを活用した異常検知システム。リアルタイムカメラストリーミングとAI分析を組み合わせた監視システムです。

## 機能

- リアルタイムカメラストリーミング
- Webブラウザでの映像確認
- 低レイテンシーなMJPEGストリーミング
- マルチスレッドによる効率的な処理
- スペースキーによる画像キャプチャ機能
  - タイムスタンプ付きで自動保存
  - キャプチャ時のフラッシュ効果

## セットアップ

### 必要条件

- Python 3.8以上
- OpenCV
- FastAPI
- uvicorn

### インストール手順

1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/AnomalyDetection.git
cd AnomalyDetection
```

2. バックエンド依存パッケージのインストール
```bash
pip install -r docker/requirements.txt
```

3. 環境変数の設定
```bash
export CAMERA_ID=1  # お使いのカメラIDに応じて設定
```

### フロントエンド開発環境のセットアップ

1. Node.js環境の準備
2. 依存パッケージのインストール
```bash
npm install
```

3. 開発サーバーの起動
```bash
docker compose up
```

4. TypeScriptファイルの変更を監視
```bash
npm run watch
```

### Docker環境での実行

```bash
docker compose up --build
```

## 使用方法

1. サーバーの起動
```bash
python -m src.main
```

2. ブラウザでアクセス
```
http://localhost:8000

3. 画像キャプチャ
- ブラウザ上でストリーミング映像を表示中に、スペースキーを押すと現在のフレームをキャプチャできます
- キャプチャした画像は `captures/` ディレクトリに自動保存されます
- ファイル名は `capture_YYYYMMDD_HHMMSS.jpg` の形式で保存されます
```

## カメラ選択機能

### 利用可能なカメラ
- PCに接続された複数のカメラをサポート
- 内蔵Webカメラ、USBカメラなどを自動検出
- カメラ情報の自動取得と表示

### 使用方法
1. アプリケーションの起動
   ```bash
   docker compose up -d
   ```

2. ブラウザでアクセス
   ```
   http://localhost:8000
   ```

3. カメラの切り替え
   - 画面上部のプルダウンメニューからカメラを選択
   - カメラの映像がリアルタイムで切り替わります
   - 切り替え時にエラーが発生した場合は画面上に表示されます

### 注意事項
- カメラデバイスへのアクセス権限が必要です
- デバイスの抜き差しを行った場合は、アプリケーションの再起動が必要な場合があります

## 技術詳細

システムの技術的な詳細については、[技術解説書](docs/technical-notes.md)をご参照ください。

## ライセンス

MIT License