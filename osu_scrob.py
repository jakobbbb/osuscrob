#!/usr/bin/env python3

import yaml
import os
import requests
import pylast
from dateutil import parser

CONFIG = {
    "osu_api_key": "",
    "osu_user": "",
    "lastfm_api_key": "",
    "lastfm_shared_secret": "",
    "lastfm_user": "",
    "lastfm_pass": "",
}


def load_config():
    script_dir = os.path.realpath(os.path.dirname(__file__))
    config_path = os.path.join(script_dir, "config.yml")
    if not os.path.exists(config_path):
        with open(config_path, "w+") as f:
            f.write(yaml.dump(CONFIG, sort_keys=True))
            print(f"Please configure in {config_path} :)")
            return None
    else:
        with open(config_path, "r") as f:
            return yaml.safe_load(f.read())


def get_recent(osu_api_key, osu_user, **_):
    base = "https://osu.ppy.sh/api"
    endpoint = "/get_user_recent"
    params = {
        "k": osu_api_key,
        "u": osu_user,
        "limit": 50,
    }

    resp = requests.get(base + endpoint, params=params)
    return resp.json()


def get_beatmap(osu_api_key, beatmap_id, **_):
    base = "https://osu.ppy.sh/api"
    endpoint = "/get_beatmaps"
    params = {
        "k": osu_api_key,
        "b": beatmap_id,
    }

    resp = requests.get(base + endpoint, params=params)
    return resp.json()[0]


def main():
    cfg = load_config()

    script_dir = os.path.realpath(os.path.dirname(__file__))
    prev_scrobs_path = os.path.join(script_dir, "prev_scrobs.lst")
    prev_scrobs = []
    if os.path.exists(prev_scrobs_path):
        with open(prev_scrobs_path, "r") as f:
            prev_scrobs = f.read().splitlines()

    if cfg is None:
        return 1

    lastfm = pylast.LastFMNetwork(
        api_key=cfg["lastfm_api_key"],
        api_secret=cfg["lastfm_shared_secret"],
        username=cfg["lastfm_user"],
        password_hash=pylast.md5(cfg["lastfm_pass"]),
    )

    recent = get_recent(**cfg)
    scrobbles = []
    for play in recent:
        beatmap_id = play["beatmap_id"]
        score = play["score"]
        if score == "F":
            continue
        beatmap = get_beatmap(**cfg, beatmap_id=beatmap_id)
        artist = beatmap["artist"]
        title = beatmap["title"]
        time = play["date"]
        timestamp = parser.parse(time + " UTC").timestamp()
        scrobble = {
            "title": title,
            "artist": artist,
            "timestamp": timestamp,
        }
        if str(scrobble) not in prev_scrobs:
            scrobbles.append(scrobble)
            prev_scrobs.append(str(scrobble))
            print(scrobble)

    with open(prev_scrobs_path, "w+") as f:
        f.write("\n".join(prev_scrobs))

    print(f"Scrobbling {len(scrobbles)} tracks!")
    lastfm.scrobble_many(scrobbles)


if __name__ == "__main__":
    exit(main())
