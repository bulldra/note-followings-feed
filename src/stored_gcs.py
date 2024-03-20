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

    def is_cached(self) -> bool:
        if self._blob.exists() and not self._is_refresh:
            return self._current_time - self.get_updated() < self._ttl
        return False

    def get_updated(self) -> datetime:
        self._blob.reload()
        return self._blob.updated
