import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

from django.conf import settings

import string

# Spotify object
client_manager = SpotifyClientCredentials(
    client_id=settings.SPOTIFY_CLIENT_ID,
    client_secret=settings.SPOTIFY_CLIENT_SECRET_ID
)

sp = spotipy.Spotify(client_credentials_manager=client_manager)


def sp_treat_string(artist: str, track: str):
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

    cover_url = None
    sp_string = sp_treat_string(artist_name, track_name)
    try:
        sp_track = sp.search(sp_string, limit=1)
    except spotipy.client.SpotifyException as e:
        print(e)
    else:
        sp_track = sp_track['tracks']['items']
        if sp_track and sp_track[0]['album']['images']:
            cover_url = sp_track[0]['album']['images'][0]['url']
    return cover_url
