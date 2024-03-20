import json
import time
import urllib

import requests

import stored_gcs


class StoredFollows(stored_gcs.StoredGcs):

    def __init__(self, bucket_name, blob_name, creator_id, is_refresh=False):
        super().__init__(bucket_name, blob_name, is_refresh=is_refresh)
        self._creator_id = creator_id
        self._follows: list = None

    def get(self) -> list:
        if self._follows:
            return self._follows
        if not self.is_expired():
            self._follows = json.loads(self.download_as_string())
            return self._follows

        base_url: str = (
            f"https://note.com/api/v2/creators/{self._creator_id}/followings"
        )
        follows: [str] = []
        for i in range(1, 100):
            params: dict = {"page": i}
            urlencode_params: str = urllib.parse.urlencode(params)
            url: str = f"{base_url}?{urlencode_params}"
            response: requests.Response = requests.get(
                url, headers={"Accept": "application/json"}, timeout=10
            )
            if response.status_code != 200:
                raise ValueError(f"Failed to get json from {url}")
            json_data: dict = json.loads(response.text)
            if not json_data["data"]:
                raise ValueError(f"Failed to get json from {url}")
            if json_data["data"]["follows"]:
                follows.extend([x["urlname"] for x in json_data["data"]["follows"]])
            if json_data["data"]["isLastPage"]:
                break
            time.sleep(0.1)
        self._follows = follows
        return self._follows

    def parsist(self) -> None:
        self._blob.upload_from_string(
            json.dumps(self.get()), content_type="application/json"
        )
