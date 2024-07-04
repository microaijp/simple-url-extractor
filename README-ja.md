[![Python versions](https://img.shields.io/pypi/pyversions/trafilatura.svg)](https://pypi.python.org/pypi/trafilatura)

# simple-url-extractor
URLを指定すると、タイトル、本文などを抽出するシンプルなAPIです。  
99% [trafilatura](https://trafilatura.readthedocs.io/en/latest/) を使用しています。


## APIコール
### リクエスト
```
curl -X 'GET' \
  'http://localhost:8002/v1/extract?url=https%3A%2F%2Fmicroai.jp%2Fblog%2F70b4bf89-fe4b-451f-ac81-2d757fca8b6a&cache_seconds=1' \
  -H 'accept: application/json'
```

### レスポンス
```
{
  "title": "Difyのバージョンが v0.6.11からv0.6.12 に上がったので、Kubernetes で運用しているDifyのバージョンアップを行ってみる | microAI",
  "author": null,
  "hostname": "microai.jp",
  "date": "2024-06-29",
  "fingerprint": "b0b37451d481f718",
  "id": null,
  "license": null,
  "comments": "",
  "raw_text": "2024/06/28 に v0.6.11 がリリースされていました。Difyは本当に素晴らしいアプリですが、不具合もまだまだ多くあるので、バージョンアップしていきます。 前回から２週間ほどでのバージョンアップ。活発で嬉しいです。 最初に Dify のバージョンアップ中に、1〜2分程度、使用できない時間が発生します。 本番運用中である場合は、お知らせを出すなどの対応が必要です。 インストール方法 まだインストールしていない方、まはたインストール方法について見たい方は を御覧ください インストール設定ファイルを修正 インストール時に作成した dify-values.yaml を修正しますが、私の場合、v0.6.10 をインストールし v0.6.11 に途中バージョンアップしています。 バージョンアップのログは、以下を御覧ください。 # nano dify-values.yaml で global: host: \"dify.microai.jp\" enableTLS: false image: tag: \"0.6.11\" を global: host: \"dify.microai.jp\" enableTLS: false image: tag: \"0.6.12\" に書き換えます。 host: \"dify.microai.jp\" の部分は、ご自身の環境のものにいてください。 バージョンアップ実行 # helm upgrade dify douban/dify -f dify-values.yaml --debug 実行すると default pod/dify-api-5c9c9b59c9-nwshd 0/1 ContainerCreating 0 26s default pod/dify-frontend-8599b488dd-b7q9r 0/1 ContainerCreating 0 26s default pod/dify-worker-78968f767-9lxqz この３つが更新されていきました。 このタイミングで、一時的に使用できなくなります。 DBをマイグレーション（変更）する コマンドを実行する対象を探す # kubectl get pod | grep dify-worker dify-worker-77d675b4b-tw8kc 1/1 Running 0 85s 実行する対象に対してマイグレーション指示を出し、マイグレーションする kubectl exec -it dify-worker-77d675b4b-tw8kc -- flask db upgrade Kubernetes 特有の修正を行う # helm get manifest dify > dify-custome-0.6.12.yaml # sed -i 's|http://dify.microai.jp|https://dify.microai.jp|g' dify-custome-0.6.12.yaml dify.microai.jp の部分は、ご自身のホスト名に置き換えてください、 Milvus 部分の修正 # nano dify-custome-0.6.12.yaml dify-custome-0.6.12.yaml の中に２箇所 - name: VECTOR_STORE value: milvus このような記載があるので、それぞれの直後に - name: VECTOR_STORE value: milvus - name: MILVUS_HOST value: \"microai-milvus.milvus.svc.cluster.local\" - name: MILVUS_PORT value: \"19530\" - name: MILVUS_USER value: \"root\" - name: MILVUS_PASSWORD value: \"Milvus\" - name: MILVUS_SECURE value: \"false\" となるように、Milvusの設定を追記します。繰り返しになりますが２箇所どちらも同じ修正を加えてください。 \"microai-milvus.milvus.svc.cluster.local\" は、皆様の環境にあわせて書き換えてください。他の項目はデフォルト値です。 設定反映 # kubectl apply -f dify-custome-0.6.12.yaml で設定を反映させていきます。 これでバージョンアップ完了です。 バージョン確認 上記のメニューからバージョンを確認して 0.6.12 と表示されているかを確認します。 おまけ v0.6.12 の CHANGELOG を流し読み 個人的に興味のあるところだけを斜め読みしてメモしていきます。 新機能 (Tracing) LangSmith と Langfuse で Difyのワークフロー 内で行われている LangChain の処理内容を見ることができるようになりました。 クライアントに提供する場合などで、不具合のデバッグなどが容易になるためありがたいですね。 新機能（Undo, Redo, Change History) ワークフロー編集画面で、もとに戻す、やり直す、変更履歴からもとに戻す。の機能が追加されました。こちらも、地味にありがたいです。 新機能 (DSLでの上書き） 今までは、作ったワークフローをDSLでエクスポートして、エクスポートしたDSLを使って、新しいワークフローを作ることはできましたが、すでにあるワークフローを上書きすることはできませんでした。それができるようになりました。 個人的には、あまり使用するケースが思いつきませんが、便利な人にとってはものすごく有用そうという印象。 新機能 (ワークフロー非表示） プレビュー機能で表示される上記の赤枠の場所の表示・非表示を切り替えられるようになりました。 エンドユーザーに見せたくないときもありますので、これは嬉しいですね。",
  "text": "2024/06/28 に v0.6.11 がリリースされていました。Difyは本当に素晴らしいアプリですが、不具合もまだまだ多くあるので、バージョンアップしていきます。\n前回から２週間ほどでのバージョンアップ。活発で嬉しいです。\n最初に\nDify のバージョンアップ中に、1〜2分程度、使用できない時間が発生します。\n本番運用中である場合は、お知らせを出すなどの対応が必要です。\nインストール方法\nまだインストールしていない方、まはたインストール方法について見たい方は\nを御覧ください\nインストール設定ファイルを修正\nインストール時に作成した dify-values.yaml\nを修正しますが、私の場合、v0.6.10 をインストールし v0.6.11 に途中バージョンアップしています。\nバージョンアップのログは、以下を御覧ください。\n# nano dify-values.yaml\nで\nglobal:\nhost: \"dify.microai.jp\"\nenableTLS: false\nimage:\ntag: \"0.6.11\"\nを\nglobal:\nhost: \"dify.microai.jp\"\nenableTLS: false\nimage:\ntag: \"0.6.12\"\nに書き換えます。\nhost: \"dify.microai.jp\"\nの部分は、ご自身の環境のものにいてください。\nバージョンアップ実行\n# helm upgrade dify douban/dify -f dify-values.yaml --debug\n実行すると\ndefault pod/dify-api-5c9c9b59c9-nwshd 0/1 ContainerCreating 0 26s\ndefault pod/dify-frontend-8599b488dd-b7q9r 0/1 ContainerCreating 0 26s\ndefault pod/dify-worker-78968f767-9lxqz\nこの３つが更新されていきました。\nこのタイミングで、一時的に使用できなくなります。\nDBをマイグレーション（変更）する\nコマンドを実行する対象を探す\n# kubectl get pod | grep dify-worker\ndify-worker-77d675b4b-tw8kc 1/1 Running 0 85s\n実行する対象に対してマイグレーション指示を出し、マイグレーションする\nkubectl exec -it dify-worker-77d675b4b-tw8kc -- flask db upgrade\nKubernetes 特有の修正を行う\n# helm get manifest dify > dify-custome-0.6.12.yaml\n# sed -i 's|http://dify.microai.jp|https://dify.microai.jp|g' dify-custome-0.6.12.yaml\ndify.microai.jp\nの部分は、ご自身のホスト名に置き換えてください、\nMilvus 部分の修正\n# nano dify-custome-0.6.12.yaml\ndify-custome-0.6.12.yaml\nの中に２箇所\n- name: VECTOR_STORE\nvalue: milvus\nこのような記載があるので、それぞれの直後に\n- name: VECTOR_STORE\nvalue: milvus\n- name: MILVUS_HOST\nvalue: \"microai-milvus.milvus.svc.cluster.local\"\n- name: MILVUS_PORT\nvalue: \"19530\"\n- name: MILVUS_USER\nvalue: \"root\"\n- name: MILVUS_PASSWORD\nvalue: \"Milvus\"\n- name: MILVUS_SECURE\nvalue: \"false\"\nとなるように、Milvusの設定を追記します。繰り返しになりますが２箇所どちらも同じ修正を加えてください。\n\"microai-milvus.milvus.svc.cluster.local\"\nは、皆様の環境にあわせて書き換えてください。他の項目はデフォルト値です。\n設定反映\n# kubectl apply -f dify-custome-0.6.12.yaml\nで設定を反映させていきます。\nこれでバージョンアップ完了です。\nバージョン確認\n上記のメニューからバージョンを確認して 0.6.12\nと表示されているかを確認します。\nおまけ v0.6.12 の CHANGELOG を流し読み\n個人的に興味のあるところだけを斜め読みしてメモしていきます。\n新機能 (Tracing)\nLangSmith と Langfuse で Difyのワークフロー 内で行われている LangChain の処理内容を見ることができるようになりました。\nクライアントに提供する場合などで、不具合のデバッグなどが容易になるためありがたいですね。\n新機能（Undo, Redo, Change History)\nワークフロー編集画面で、もとに戻す、やり直す、変更履歴からもとに戻す。の機能が追加されました。こちらも、地味にありがたいです。\n新機能 (DSLでの上書き）\n今までは、作ったワークフローをDSLでエクスポートして、エクスポートしたDSLを使って、新しいワークフローを作ることはできましたが、すでにあるワークフローを上書きすることはできませんでした。それができるようになりました。\n個人的には、あまり使用するケースが思いつきませんが、便利な人にとってはものすごく有用そうという印象。\n新機能 (ワークフロー非表示）\nプレビュー機能で表示される上記の赤枠の場所の表示・非表示を切り替えられるようになりました。\nエンドユーザーに見せたくないときもありますので、これは嬉しいですね。",
  "language": null,
  "image": "https://microai.jp/images/ogimage.webp",
  "pagetype": null,
  "filedate": "2024-07-04",
  "source": "https://microai.jp/blog/70b4bf89-fe4b-451f-ac81-2d757fca8b6a",
  "source_hostname": "Microai",
  "excerpt": null,
  "categories": "",
  "tags": "microAI,AI,API"
}
```

## pipenv を使ったセットアップ
```
$ cd /path/to/this-app
$ pipenv shell
$ pipenv install
```

## ローカル起動
```
$ cd /path/to/this-app
$ cd app
$ uvicorn main:app --reload --port 8002
```
http://localhost:8002/docs にブラウザでアクセス  
ポートは、`app/main.py` で変更可能です

## Docker
### Dockerイメージのビルド
```
$ cd /path/to/this-app
$ docker build -t simple-url-extractor .
```

### Dockerコンテナの起動
```
$ cd /path/to/this-app
$ docker-compose up -d
```
http://localhost:8002/docs にブラウザでアクセス  
ポートは、`docker-compose.yml` で変更可能です