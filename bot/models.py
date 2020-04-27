from django.db import models
from django.conf import settings
from django.utils.timezone import now
from .managers import MessageManager, TrackManager
from .musixmatch import track_search
from .statistics import stats_text
from .choices import CommandTypes, MessageEventTypes
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
        msg = "*Tus canciones favoritas* :o \n"
        for favorite in self.favorites.all():
            msg += "- %s\n" % str(favorite)
        return msg

    def __str__(self):
        return self.psid

class UserSession(models.Model):
    """
    """

    user = models.ForeignKey('BotUser', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True)

    @classmethod
    def save_user_session(cls, sender):

        is_new_session = True
        sessions = cls.objects.filter(user__id=sender.id)

        if sessions.exists():
            last_session = sessions.order_by('end_time').last()
            if now() - last_session.end_time <= settings.SESSION_TIME_THRESHOLD:
                is_new_session = False
                last_session.save()

        if is_new_session:
            cls.objects.create(user=sender)

    def __str__(self):
        return str(self.start_time) + " to " + str(self.end_time)

class MessageEvent(models.Model):
    """
    """

    text = models.TextField(blank=True)
    sender = models.ForeignKey('BotUser', on_delete=models.CASCADE)
    type = models.CharField(max_length=2,
        choices=MessageEventTypes.CHOICES, default=MessageEventTypes.LYRICS
    )

    objects = MessageManager()

    def handle_event(self):
        """
        """
        msg = ''

        if self.type == MessageEventTypes.LYRICS:
            mxm = track_search(self.text)

            if mxm.status == 200:
                if mxm.tracks:
                    mxm.tracks = mxm.tracks[:settings.DEFAULT_RECORDS_SIZE]
                    return self.sender.send_list_tracks(mxm.tracks)
                else:
                    msg = "No encontramos canciones :("
            else:
                msg = "Ups, tuvimos inconvenientes en la búsqueda :o"

        elif self.type == MessageEventTypes.FAVORITE:
            track = self.related_track
            favorites = self.sender.favorites.filter(
                commontrack_id=track.commontrack_id
            )
            if favorites.exists():
                msg = "*%s* sigue siendo tu favorita :)" % track.track_name
            else:
                self.sender.favorites.add(track)
                msg = "Guardamos *%s* como tu favorita!" % track.track_name

        elif self.type == MessageEventTypes.COMMAND:
            if self.text == CommandTypes.STATISTICS:
                msg = stats_text()
            elif self.text == CommandTypes.FAVORITES:
                msg = self.sender.favorites_text()
            else:
                command_types_repr = ', '.join(
                    ["*%s*" %command for command in CommandTypes.LIST]
                )
                msg = "Prueba con los comandos %s :)" %command_types_repr

        self.sender.send_text(msg)

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
