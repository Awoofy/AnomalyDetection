# カメラアプリケーション テスト・動作確認手順

## 1. テスト環境の準備

### 必要なパッケージのインストール
```bash
pip install pytest pytest-asyncio fastapi[test]
```

### Dockerコンテナでのカメラアクセス
```bash
docker compose up --build
```

## 2. ユニットテストの実行

### カメラ機能のテスト
```bash
python -m pytest tests/test_camera.py -v
```

### APIエンドポイントのテスト
```bash
python -m pytest tests/test_api.py -v
```

## 3. 手動動作確認手順

### 1) カメラデバイスの認識確認
- [ ] `ls /dev/video*` でカメラデバイスの存在を確認
- [ ] デバイスのアクセス権限を確認

### 2) アプリケーションの起動
- [ ] `python src/main.py` でアプリケーションを起動
- [ ] http://localhost:8000 にアクセス
- [ ] ブラウザでカメラ映像が表示されることを確認

### 3) ストリーミング機能の確認
- [ ] フレームレートが安定していること（20FPS以上）
- [ ] 画質が適切であること
- [ ] 遅延が最小限であること（500ms以下）

### 4) エラーケースの確認
- [ ] カメラを抜き差しした際の挙動
  - エラーメッセージが表示される
  - 再接続時に自動復帰する
- [ ] アプリケーション再起動時の動作
  - カメラリソースが正しく解放される
  - 再起動後に正常に動作する
- [ ] 無効なURLアクセス時のエラー応答
  - 404エラーページが表示される

## 4. 性能測定とモニタリング

### メモリ使用量の監視
```bash
# メモリ使用量の確認
ps aux | grep python

# 継続的なメモリ監視（5秒間隔）
watch -n 5 'ps aux | grep python'
```

### CPU使用率の監視
```bash
# CPU使用率の確認
top -p $(pgrep -f "python.*main.py")

# CPU使用率の記録（1分間）
mpstat 5 12
```

### ネットワークパフォーマンス
```bash
# ストリーミング時のネットワーク使用量
iftop -i lo

# レイテンシの測定
curl -w "@curl-format.txt" -o /dev/null -s "http://localhost:8000/video_feed"
```

## 5. 合格基準

### 機能要件
- [ ] すべてのユニットテストが成功
- [ ] カメラデバイスが正常に認識される
- [ ] ストリーミングが安定して動作
- [ ] エラー時に適切なメッセージを表示

### 性能要件
- [ ] メモリリークがないこと
- [ ] CPU使用率が50%以下で安定
- [ ] ストリーミングのレイテンシが500ms以下
- [ ] フレームレートが20FPS以上

### セキュリティ要件
- [ ] カメラアクセス権限が適切に設定
- [ ] 無効なURLに対して適切なエラーレスポンス
- [ ] リソースが適切に解放される

## 6. トラブルシューティング

### よくある問題と解決方法

1. カメラアクセスエラー
```bash
# デバイスの権限確認
ls -l /dev/video*
# 権限の修正
sudo chmod 666 /dev/video0
```

2. ポートアクセスエラー
```bash
# 使用中のポートの確認
sudo lsof -i :8000
# プロセスの終了
sudo kill -9 <PID>
```

3. メモリリーク発生時
```bash
# メモリ使用量の詳細確認
memory_profiler main.py
# プロセスの強制終了
pkill -f "python.*main.py"