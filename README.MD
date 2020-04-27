
# Musix Match Messenger - m3bot

[Messenger](https://developers.facebook.com/docs/messenger-platform) bot that receives some lyrics and
searches for related songs in the [Musixmatch API](https://developer.musixmatch.com/) delivering the
top results. For the album cover art the [Spotify API](https://developer.spotify.com/) is beign used.

# Command Types
- */favs*: List user favorite songs.
- */stats*: Show statistics about app usage.
- *general text*: Searches for related songs and artists.

# Prerequisites
- [virtualenv](https://virtualenv.pypa.io/en/latest/)
- [postgresql](http://www.postgresql.org/)

# Before
- Install Python3.6

```bash
sudo apt-get install python3.6-dev build-essential
```

- Install pip and virtualenv 
```
sudo apt install python3-pip
sudo pip3 install virtualenv 
```

- Install postgresql and postgis
```bash
sudo apt-get install postgresql postgresql-contrib postgis
```

# Initialize the project
```bash
virtualenv env
source env/bin/activate
```
Install dependencies:

```bash
pip install -r requirements.txt
```
Create the database:

```bash
sudo -u postgres createdb m3db 
```

Migrate the database:
```bash
python urbaner/manage.py migrate
```
