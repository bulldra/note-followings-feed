import json

import stored_gcs


class StoredEtagMap(stored_gcs.StoredGcs):
    def __init__(self, bucket_name, blob_name):
        super().__init__(bucket_name, blob_name)
        self._etag_map = None

    def get(self) -> dict:
        if self._etag_map:
            return self._etag_map
        if self._blob.exists():
            self._etag_map = json.loads(self._blob.download_as_text())
        else:
            self._etag_map = {}
        return self._etag_map

    def get_etag(self, url) -> str:
        return self.get().get(url)

    def put_etag(self, url, etag) -> None:
        self.get()[url] = etag

    def parsist(self) -> None:
        self._blob.upload_from_string(
            json.dumps(self.get()), content_type="application/json"
        )
