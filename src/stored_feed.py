import feedparser

import stored_gcs


class StoredFeed(stored_gcs.StoredGcs):
    def __init__(self, bucket_name, blob_name):
        super().__init__(bucket_name, blob_name)
        self._feed_dict = None
        self._feed_str = None

    def get(self) -> feedparser.FeedParserDict | None:
        if self._feed_dict:
            return self._feed_dict
        if self.is_exists():
            self._feed_str = self.download_as_string()
            self._feed_dict: feedparser.FeedParserDict = feedparser.parse(
                self._feed_str
            )
        else:
            self._feed_dict = None
        return self._feed_dict

    def get_as_string(self) -> str | None:
        self.get()
        return self._feed_str

    def parsist(self, feed_str: str) -> None:
        self._blob.upload_from_string(feed_str, content_type="application/rss+xml")
