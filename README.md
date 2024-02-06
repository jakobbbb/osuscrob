# osu_scrob
*a last.fm scrobbler for osu!*

## what

fetches your recent osu~ plays and scrobbles them to last.fm
(unless you ranked 'F')

## setup

run `poetry install --no-root` to install dependencies

run `poetry run osu_scrob.py` once, then add everything to
`config.yml`.

Notes:
* `osu_api_key`:  Create an app using *Legacy API* at
   https://osu.ppy.sh/p/api
* `lastfm_api_key` and `lastfm_shared_secret`:
  create and app at https://www.last.fm/api/account/create
* `lastfm_pass` is your actual login password

## how

after you've finished playing, or periodically throughout, run the
script
