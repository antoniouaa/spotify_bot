# SpotifyBot is now brought into this cruel world

Syke!

29/09/2020

---

[![Build Status](https://travis-ci.com/antoniouaa/spotify_bot.svg?branch=master)](https://travis-ci.com/antoniouaa/spotify_bot)

Copy the example config file in [/misc](/misc) and place it in the project root dir

```shell
python -m music_bot config.ini
```

With docker,

```shell
docker build --tag music_bot .
docker run -d --name music_bot
```

To run tests,

```shell
python -m unittest discover -b
```

### Issues with packages

If spotipy gives you a hard time, spank it's maintainers at [plamere/spotipy](https://github.com/plamere/spotipy).
Then install from github with `pip install git+https://github.com/plamere/spotipy.git --upgrade`

If pymongo gives you a hard time, do the same at [mongodb/mongo-python-driver](https://github.com/mongodb/mongo-python-driver).
Then install `dnspython` with `pip install dnspython`
