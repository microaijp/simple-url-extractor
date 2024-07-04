[![Python versions](https://img.shields.io/pypi/pyversions/trafilatura.svg)](https://pypi.python.org/pypi/trafilatura)

# simple-url-extractor
URLを指定すると、タイトル、本文などを抽出するシンプルなAPIです。


## Docker
```
pip freeze > ./requirements.txt

# Dockerイメージのビルド
docker build -t simple-url-extractor .

# Dockerコンテナの起動
docker run -d --name simple-url-extractor -p 8200:8002 simple-url-extractor
```