import json

from note_follow_feed import NoteFollowFeed


def test_execute():
    with open("./tests/config.json", "r", encoding="utf-8") as json_file:
        config: dict = json.load(json_file)
    note_follow_feed = NoteFollowFeed(config)
    print(note_follow_feed.execute("bulldra"))


def test_get_user_feed():
    with open("./tests/config.json", "r", encoding="utf-8") as json_file:
        config: dict = json.load(json_file)
    note_follow_feed = NoteFollowFeed(config)
    print(note_follow_feed.get_user_feed("bulldra"))
