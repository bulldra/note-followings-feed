import json
import logging

import flask
import functions_framework
import google.cloud.logging

from note_follow_feed import NoteFollowFeed

app: flask.Flask = flask.Flask(__name__)


@functions_framework.http
def main(request: flask.Request):
    logging_client: google.cloud.logging.Client = google.cloud.logging.Client()
    logging_client.setup_logging()
    logger: logging.Logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    if request.method == "HEAD":
        logger.debug("HEAD %s", request.url)
        return ("", 200)
    if request.method != "GET":
        return ("Only GET requests are accepted", 405)
    if request.args.get("creator_id") is None:
        return ("Missing required parameter 'creator_id'", 400)
    creator_id: str = request.args.get("creator_id")
    logger.debug("creator_id: %s", creator_id)

    with open("./config.json", "r", encoding="utf-8") as json_file:
        config: dict = json.load(json_file)
    feed: NoteFollowFeed = NoteFollowFeed(config)
    return flask.Response(feed.execute(creator_id), 200, mimetype="application/rss+xml")
