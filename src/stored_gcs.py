from datetime import datetime, timedelta, timezone

from google.cloud import storage


class StoredGcs:

    def __init__(
        self, bucket_name, blob_name, ttl=timedelta(hours=2), is_refresh=False
    ):
        self._blob = storage.Client().get_bucket(bucket_name).blob(blob_name)
        self._current_time: datetime = datetime.now(timezone.utc)
        self._ttl = ttl
        self._is_refresh = is_refresh

    def is_exists(self) -> bool:
        return self._blob.exists()

    def is_expired(self) -> bool:
        if self.is_exists() and not self._is_refresh:
            return self._current_time - self.get_updated() > self._ttl
        return True

    def get_updated(self) -> datetime | None:
        if self.is_exists():
            self._blob.reload()
            return self._blob.updated
        return None

    def download_as_string(self) -> str | None:
        if self.is_exists():
            return self._blob.download_as_text()
        return None
