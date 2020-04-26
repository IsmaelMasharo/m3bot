from django.db import models
from django.conf import settings
from .managers import MessageManager, TrackManager
import datetime
import requests

class BotUser(models.Model):
    """
    """
    psid = models.TextField(unique=True)
    favorites = models.ManyToManyField('MxmTrack')

    def _build_message(self):
        msg = {
            'recipient': {'id': self.psid}
        }
        return msg

    def _send(self, msg):
        response = requests.post(settings.FB_URL, json=msg)

    def send_action(self, action):
        msg = self._build_message()
        msg['sender_action'] = action
        self._send(msg)

    def send_text(self, text):
        msg = self._build_message()
        msg['message'] = {'text': text}
        msg['messaging_type'] = 'RESPONSE'
        self._send(msg)

    def send_list_tracks(self, tracks):
        msg = self._build_message()
        msn_tracks = [track.messenger_track(self) for track in tracks]
        msg['message'] = {
            'attachment': {
                'type': 'template',
                'payload': {
                    'template_type': 'generic',
                    'sharable': 'true',
                    'elements': msn_tracks
                }
            }
        }
        self._send(msg)

    def favorites_text(self):
        msg = "These are your favorite songs:\n"
        for favorite in self.favorites.all():
            msg += "- " + str(favorite) + "\n"
        return msg

    def __str__(self):
        return self.psid

class UserSession(models.Model):
    """
    """

    user = models.ForeignKey('BotUser', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True)

    @property
    def duration(self):
        return self.end_time - self.start_time

    def __str__(self):
        return str(self.start_time) + " to " + str(self.end_time)


class MessageEvent(models.Model):
    """
    """

    LYRICS = 'LY'
    FAVORITE = 'FA'
    COMMAND = 'CO'
    MESSAGE_TYPES = (
        (LYRICS, 'Lyrics'),
        (COMMAND, 'Command'),
        (FAVORITE, 'Favorite')
    )

    text = models.TextField(blank=True)
    type = models.CharField(max_length=2, choices=MESSAGE_TYPES, default=LYRICS)
    sender = models.ForeignKey('BotUser', on_delete=models.CASCADE)

    objects = MessageManager()

    def __str__(self):
        return self.text

class MxmTrack(models.Model):
    """
    """
    commontrack_id = models.PositiveIntegerField(primary_key=True)
    track_name = models.TextField()
    artist_name = models.TextField()
    vanity_id = models.TextField()
    album_id = models.PositiveIntegerField()
    album_name = models.TextField()
    artist_id = models.PositiveIntegerField()
    image_url = models.URLField(null=True, max_length=500)
    track_url = models.URLField(default='https://www.musixmatch.com/', max_length=500)

    objects = TrackManager()

    def messenger_track(self, user):
        """
        :return: Dictionary in the Facebook-required template form.
        """
        msg = {
            'title': str(self.artist_name) + " - " + str(self.track_name),
            'image_url': str(self.image_url),
            'subtitle': str(self.album_name),
            'default_action': {
                'type': 'web_url',
                'url': str(self.track_url),
                'messenger_extensions': 'false',
                'webview_height_ratio': 'tall'
            }
        }

        if not user.favorites.filter(commontrack_id=self.commontrack_id).exists():
            msg['buttons'] = [{
                'type': 'postback',
                'title': 'Favorite',
                'payload': str(self.commontrack_id)
            }]

        return msg

    def __str__(self):
        return str(self.artist_name) + " - " + str(self.track_name)
