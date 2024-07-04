# ベースイメージを指定
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /app

RUN apt-get update

COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir --upgrade -r requirements.txt


COPY ./app/ .

EXPOSE 8002

# コンテナ起動時に実行するコマンドを設定
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]
