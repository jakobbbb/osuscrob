# osu_scrob
*an osu! scrobbler*

## what

fetches your recent plays and scrobbles them (unless you ranked 'F')

## deps
* `pylast`
* `dateutil`

## how

run `./osu_scrob.py` once, then add everything to
`config.yml`.

Notes:
* `osu_api_key`:  Create an app at https://osu.ppy.sh/p/api
* `lastfm_api_key` and `lastfm_shared_secret`:
  create and app at https://www.last.fm/api/account/create
* `lastfm_pass` is your login password
