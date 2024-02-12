# osu_scrob
*a last.fm scrobbler for osu!*

## what

fetches your recent osu~ plays and scrobbles them to last.fm
(unless you ranked 'F')

## setup

either:
run `poetry install` to install dependencies,
then run the script with `poetry run osuscrob`.

or:
install the script and deps with `pipx install .`,
then run simply as `osuscrob`.

run the script once, then add everything to
`~/.config/osuscrob/config.yml`.

Notes:
* `osu_client_id` and `osu_client_secret`:  Create a new *OAuth
  Application* at https://osu.ppy.sh/p/api
* `lastfm_api_key` and `lastfm_shared_secret`:
  create and app at https://www.last.fm/api/account/create
* `lastfm_pass` is your actual login password

## how

after you've finished playing, or periodically throughout, run the
script
