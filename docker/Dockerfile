FROM python:3.11-slim

# システムの依存関係をインストール
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    curl \
    gnupg \
    v4l-utils \
    && rm -rf /var/lib/apt/lists/*

# Node.jsをインストール
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# 作業ディレクトリを設定
WORKDIR /app

# npmのキャッシュディレクトリを作成し、パーミッションを設定
RUN mkdir -p /app/.npm && \
    chown -R 1000:1000 /app/.npm

# package.jsonとTypeScript設定ファイルをコピー
COPY package.json tsconfig.json webpack.config.js ./

# node_modulesディレクトリを作成し、パーミッションを設定
RUN mkdir -p /app/node_modules && \
    chown -R 1000:1000 /app/node_modules

# requirements.txtをコピー
COPY docker/requirements.txt .

# uvを使用してPythonパッケージをインストール
ENV PYTHON_ENV=development
RUN python -m pip install -U pip uv && \
    uv pip install --system --no-cache -r requirements.txt

# ソースコードをコピー
COPY src ./src

# TypeScriptをビルド
RUN npm install && \
    npm run build && \
    chown -R 1000:1000 /app

# 開発用ポートを公開
EXPOSE 8000

# FastAPIサーバーを起動
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app/src"]