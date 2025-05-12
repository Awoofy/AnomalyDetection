FROM python:3.11-slim

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /app

# requirements.txtをコピー
COPY docker/requirements.txt .

# uvを使用してPythonパッケージをインストール
ENV PYTHON_ENV=development
RUN python -m pip install -U pip uv && \
    uv pip install --system --no-cache -r requirements.txt

# 開発用ポートを公開
EXPOSE 8000

# FastAPIサーバーを起動
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app/src"]