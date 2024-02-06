#!/usr/bin/env python3

from ossapi.models import Beatmapset, Score, Grade
import yaml
import re
import os
import requests
import pylast
from ossapi import Ossapi, Domain
from typing import List

CONFIG = {
    "osu_client_id": "",
    "osu_client_secret": "",
    "osu_user": "",
    "osu_lazer": False,
    "lastfm_api_key": "",
    "lastfm_shared_secret": "",
    "lastfm_user": "",
    "lastfm_pass": "",
}

SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.yml")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        write_config(CONFIG)
        print(f"Please configure in {CONFIG_PATH} :)")
        return None
    else:
        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f.read())


def check_config(cfg):
    keys_missing = set(CONFIG.keys()) - set(cfg.keys())
    if len(keys_missing) > 0:
        print("Missing the following config keys:")
        for k in keys_missing:
            print(f"  - {k}")
            cfg[k] = CONFIG[k]
        write_config(cfg)
        return False

    keys_empty = []
    for k, v in cfg.items():
        if v is None or len(str(v)) == 0:
            keys_empty.append(k)
    if len(keys_empty) > 0:
        print("The following config options must not be empty:")
        [print(f"  - {k}") for k in keys_empty]
        return False

    return True


def write_config(cfg):
    with open(CONFIG_PATH, "w+") as f:
        f.write(yaml.dump(cfg, sort_keys=True))


def get_recent(api, osu_user, **_) -> List[Score]:
    user_id = api.user(osu_user).id
    recent = api.user_scores(
        user_id=user_id, limit=50, include_fails=False, type="recent"
    )
    return recent


def get_beatmap(api: Ossapi, beatmap) -> Beatmapset:
    return api.beatmapset(beatmap)


def filter_title(title):
    r = re.compile(r"[ ]\(tv size\)", re.IGNORECASE)
    return r.sub("", title)


def main():
    cfg = load_config()
    if not check_config(cfg):
        print(f"Please fix the config ({CONFIG_PATH}) and re-run :>")
        return 1

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

    domain = Domain.LAZER if cfg["osu_lazer"] else Domain.OSU
    api = Ossapi(cfg["osu_client_id"], cfg["osu_client_secret"], domain=domain)

    recent = get_recent(api, **cfg)
    scrobbles = []
    for play in recent:
        if play.rank == Grade.F or str(play) in prev_scrobs:
            continue
        if play.beatmapset is None:
            continue
        artist = play.beatmapset.artist
        title = play.beatmapset.title
        timestamp = play.created_at.timestamp()
        scrobble = {
            "title": filter_title(title),
            "artist": artist,
            "timestamp": timestamp,
        }
        if str(scrobble) not in prev_scrobs:
            scrobbles.append(scrobble)
            prev_scrobs.append(str(scrobble))
            prev_scrobs.append(str(play))
            print(scrobble)

    print(f"Scrobbling {len(scrobbles)} tracks!")
    lastfm.scrobble_many(scrobbles)

    with open(prev_scrobs_path, "w+") as f:
        f.write("\n".join(prev_scrobs))


if __name__ == "__main__":
    exit(main())
