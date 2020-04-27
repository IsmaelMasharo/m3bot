import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from django.conf import settings

import string
import logging

logger = logging.getLogger(__name__)

# Spotify object
client_manager = SpotifyClientCredentials(
    client_id=settings.SPOTIFY_CLIENT_ID,
    client_secret=settings.SPOTIFY_CLIENT_SECRET_ID
)

sp = spotipy.Spotify(client_credentials_manager=client_manager)


def parse_artist_track(artist, track):
    """
    Takes two strings, for artist name and track name, and returns a string that
    Spotify will easily search in its database.
    """
    try:
        artist = artist.split("feat", 1)[0]
        artist = artist.split("(", 1)[0]
        artist = artist.split("[", 1)[0]
        artist = artist.split(",", 1)[0]
        track = track.split("(", 1)[0]
        track = track.split("[", 1)[0]
        track = track.split("-", 1)[0]
    except IndexError:
        pass
    for char in string.punctuation:
        track = track.replace(char, ' ')
    return artist + " " + track


def get_cover_data(artist_name, track_name):
    """
    """

    cover_url = None
    parsed_track = parse_artist_track(artist_name, track_name)
    try:
        track = sp.search(parsed_track, limit=1)
    except spotipy.client.SpotifyException as e:
        logger.exception("Spotify provider exception. %s" % str(e))
    else:
        track = track['tracks']['items']
        if track and track[0]['album']['images']:
            cover_url = track[0]['album']['images'][0]['url']
    return cover_url
