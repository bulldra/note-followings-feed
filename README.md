## note.com Follow Feed アグリゲーター

-   概要
    -   note.com でフォローしているユーザーの RSS を集約生成
    -   Google Cloud Functions の利用を想定
-   機能
    -   note.com の指定クリエーターのフォロー一覧を取得
    -   フォローユーザーの RSS の更新を確認
    -   更新のあったユーザー RSS のうち現在から 1 時間以内のエントリのみピックアップ

## 処理シーケンス

```mermaid
sequenceDiagram
	actor A as User
	participant B1 as Slack
	participant B2 as Slack RSS App
	box this service
		participant C1 as Note Follow Feed Agg(GCF)
		participant C2 as Feed Etag Map(GCS)
	end
	participant D as note.com
	B2->>+C1: polling by scheduled
	C1->>C2: request stored feed
	C2-->>C1: response stored feed
	alt stored feed is new
		C1-->>B2: response stored feed
	else stored feed is old
		C1->>+D: request follow list
		D-->>C1: response follow list
		C1->>C2: request feed etag map
		C2-->>C1: response feed etag map
		C1->>D: request follow feed If-None-Match
		alt etag match
			D-->>C1: HTTP Status 304 with empty body
		else etag not match
			D-->>C1: HTTP Status 200 with feed body
		end
		C1->>C1: pick up and aggregate feed
		C1->>C2: parsist feed / etag map
		C1-->>-B2: response generate feed
	end
	B2->>B2: check new feed items
	alt new feed items
		B2->>B1: post feed items
		B1->>A: notification
	end

```

## 利用方法

https://{デプロイ URL}?creator_id={note_creator_id}
