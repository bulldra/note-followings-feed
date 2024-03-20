import logging
import time
from datetime import datetime, timedelta, timezone

import feedparser
import google.cloud.logging
from feedgen.feed import FeedGenerator

from stored_etag_map import StoredEtagMap
from stored_feed import StoredFeed
from stored_follows import StoredFollows


class NoteFollowFeed:

    def __init__(self, config: dict) -> None:
        logging_client: google.cloud.logging.Client = google.cloud.logging.Client()
        logging_client.setup_logging()
        self._logger: logging.Logger = logging.getLogger(__name__)
        self._logger.setLevel(logging.DEBUG)
        self._gcs_bucket_name: str = config["gcs_bucket_name"]
        self._gcs_root_dir: str = config["gcs_root_dir"]
        self._max_feed_count: int = config["max_feed_count"]
        self._etag_map: StoredEtagMap = StoredEtagMap(
            self._gcs_bucket_name, f"{self._gcs_root_dir}/etag_map.json"
        )

    def execute(self, creator_id: str) -> str:
        if creator_id is None:
            raise ValueError("creator_id is None")

        stored_feed: StoredFeed = StoredFeed(
            self._gcs_bucket_name,
            f"{self._gcs_root_dir}/feed/{creator_id}.rss",
        )
        if not stored_feed.is_expired():
            self._logger.debug("Cached Feed %s.", stored_feed.get_updated())
            return stored_feed.get_as_string()

        stage_entries: list = []
        if stored_feed.get():
            stage_entries.extend(stored_feed.get().entries)

        stored_follows: StoredFollows = StoredFollows(
            self._gcs_bucket_name,
            f"{self._gcs_root_dir}/follows/{creator_id}.json",
            creator_id,
        )
        count_200: int = 0
        count_304: int = 0
        now: datetime = datetime.now(timezone.utc)
        for follow in stored_follows.get():
            feed: feedparser.FeedParserDict | None = self.get_user_feed(follow)
            if feed and feed.status == 200:
                count_200 += 1
                for entry in feed.entries:
                    etime: datetime = datetime.fromtimestamp(
                        time.mktime(entry.published_parsed), timezone.utc
                    )
                    if now - etime < timedelta(days=1):
                        entry.title = f"{entry.title} - {feed.feed.title}"
                        stage_entries.append(entry)
                        if len(stage_entries) > self._max_feed_count * 2:
                            break
            elif feed and feed.status == 304:
                count_304 += 1
            else:
                self._logger.warning("Failed to get feed from %s", follow)
        self._logger.debug("count 200: %d, count 304: %d", count_200, count_304)

        seen_links = set()
        entries = list(
            filter(
                lambda x: x.link not in seen_links and not seen_links.add(x.link),
                stage_entries,
            )
        )

        entries = sorted(
            sorted(entries, key=lambda x: x.published_parsed, reverse=True)[
                : self._max_feed_count
            ],
            key=lambda x: x.published_parsed,
            reverse=False,
        )

        fg = FeedGenerator()
        fg.title(f"note.com following - {creator_id}")
        fg.link(href=f"https://note.com/{creator_id}/rss", rel="self")
        fg.description(fg.title())
        fg.pubDate(datetime.now(timezone.utc))
        for entry in entries:
            fe = fg.add_entry()
            fe.title(entry.title)
            fe.link(href=entry.link)
            fe.published(entry.published)

        feed_str: str = fg.rss_str(pretty=True).decode("utf-8")
        stored_feed.parsist(feed_str)
        stored_follows.parsist()
        self._etag_map.parsist()
        return feed_str

    def get_user_feed(self, user_id: str) -> feedparser.FeedParserDict | None:
        if user_id is None:
            raise ValueError("user_id is None")
        url: str = f"https://note.com/{user_id}/rss"
        etag: str = self._etag_map.get_etag(url)
        result: feedparser.FeedParserDict = feedparser.parse(url, etag=etag)
        if result.get("status") not in [200, 304]:
            return None
        if result.get("status") == 200:
            self._etag_map.put_etag(url, result.get("etag"))
            time.sleep(0.1)
        return result
