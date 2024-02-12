#!/usr/bin/env python3

from ossapi.models import Beatmapset, Score, Grade
import yaml
import re
import os
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


class OsuScrob:
    def __init__(self):
        self.dir = os.path.expanduser("~/.config/osuscrob")
        if not os.path.exists(self.dir):
            os.mkdir(self.dir)

        self.prev_scrobs_path = os.path.join(self.dir, "prev_scrobs.lst")
        self.config_path = os.path.join(self.dir, "config.yml")

        self.cfg = self.load_config()
        if not self.check_config(self.cfg):
            raise Exception(
                (f"Please fix the config ({self.config_path}) and re-run :>")
            )

        self.prev_scrobs = []
        if os.path.exists(self.prev_scrobs_path):
            with open(self.prev_scrobs_path, "r", encoding="utf-8") as f:
                self.prev_scrobs = f.read().splitlines()

        assert self.cfg
        self.init_lastfm_api(**self.cfg)
        self.init_osu_api(**self.cfg)

    def load_config(self):
        if not os.path.exists(self.config_path):
            self.write_config(CONFIG)
            print(f"Please configure in {self.config_path} :)")
            return None
        else:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f.read())

    def check_config(self, cfg):
        keys_missing = set(CONFIG.keys()) - set(cfg.keys())
        if len(keys_missing) > 0:
            print("Missing the following config keys:")
            for k in keys_missing:
                print(f"  - {k}")
                cfg[k] = CONFIG[k]
            self.write_config(cfg)
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

    def write_config(self, cfg):
        with open(self.config_path, "w+", encoding="utf-8") as f:
            f.write(yaml.dump(cfg, sort_keys=True))

    def init_lastfm_api(
        self,
        lastfm_api_key,
        lastfm_shared_secret,
        lastfm_user,
        lastfm_pass,
        **_,
    ):
        assert self.cfg

        self.lastfm = pylast.LastFMNetwork(
            api_key=lastfm_api_key,
            api_secret=lastfm_shared_secret,
            username=lastfm_user,
            password_hash=pylast.md5(lastfm_pass),
        )

    def init_osu_api(self, osu_client_id, osu_client_secret, **_):
        assert self.cfg

        domain = Domain.LAZER if self.cfg["osu_lazer"] else Domain.OSU
        self.osu = Ossapi(
            osu_client_id,
            osu_client_secret,
            domain=domain,
        )

    def get_recent(self, api, osu_user, **_) -> List[Score]:
        user_id = api.user(osu_user).id
        recent = api.user_scores(
            user_id=user_id, limit=50, include_fails=False, type="recent"
        )
        return recent

    def get_beatmap(self, api: Ossapi, beatmap) -> Beatmapset:
        return api.beatmapset(beatmap)

    def filter_title(self, title):
        r = re.compile(r"[ ]\(tv size\)", re.IGNORECASE)
        return r.sub("", title)

    def main(self):
        assert self.cfg

        recent = self.get_recent(self.osu, **self.cfg)
        scrobbles = []
        for play in recent:
            if play.rank == Grade.F or str(play) in self.prev_scrobs:
                continue
            if play.beatmapset is None:
                continue
            artist = play.beatmapset.artist
            title = play.beatmapset.title
            if play.beatmapset.title_unicode:
                title = play.beatmapset.title_unicode
            timestamp = play.created_at.timestamp()
            scrobble = {
                "title": self.filter_title(title),
                "artist": artist,
                "timestamp": timestamp,
            }
            if str(scrobble) not in self.prev_scrobs:
                scrobbles.append(scrobble)
                self.prev_scrobs.append(str(scrobble))
                self.prev_scrobs.append(str(play))
                print(scrobble)

        print(f"Scrobbling {len(scrobbles)} tracks!")
        self.lastfm.scrobble_many(scrobbles)

        with open(self.prev_scrobs_path, "w+", encoding="utf-8") as f:
            f.write("\n".join(self.prev_scrobs))


def main():
    return OsuScrob().main()


if __name__ == "__main__":
    exit(main())
