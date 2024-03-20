import json

from stored_follows import StoredFollows


def test_get_follows():

    with open("./tests/config.json", "r", encoding="utf-8") as json_file:
        config: dict = json.load(json_file)
    gcs_bucket_name: str = config["gcs_bucket_name"]
    gcs_root_dir: str = config["gcs_root_dir"]

    note_follow_feed = StoredFollows(
        gcs_bucket_name,
        f"{gcs_root_dir}/follows/bullra.json",
        "bulldra",
        is_refresh=False,
    )
    print(note_follow_feed.is_cached())
    print(note_follow_feed.get())
    note_follow_feed.parsist()
