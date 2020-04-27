from django.db import models
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings
from .spotify import get_cover_data
from .choices import MessageEventTypes
import logging

logger = logging.getLogger(__name__)

class MessageManager(models.Manager):

    def create_message(self, query):
        from .models import BotUser, MessageEvent, MxmTrack, UserSession

        [messaging] = query['entry'][-1]['messaging']

        hook_type = next(
            (key for key in messaging if key in settings.SUPPORTED_FB_HOOKS), 
            None
        )

        if not hook_type:
            raise ValueError("Hook type not implemented.")

        if query.get('object') != 'page':
            raise ValueError("page attribute not found.")

        psid = messaging['sender']['id']
        sender, _ = BotUser.objects.get_or_create(psid=str(psid))
        UserSession.save_user_session(sender)

        event = MessageEvent(sender=sender)
        hook_payload = messaging[hook_type]

        if hook_type == settings.MESSAGE_HOOK:
            message_text = hook_payload['text']

            event_type = MessageEventTypes.LYRICS
            if (
                message_text[settings.COMMAND_INDEX_AT] == \
                settings.COMMAND_IDENTIFIER
            ):
                event_type = MessageEventTypes.COMMAND

            event.text = message_text
            event.type = event_type

        elif hook_type == settings.POSTBACK_HOOK:
            commontrack_id = hook_payload['payload']
            try:
                track = MxmTrack.objects.get(commontrack_id=commontrack_id)
            except ObjectDoesNotExist:
                logger.warning("MxmTrack not being correctly saved when fetched.")
                raise ObjectDoesNotExist
            else:
                event.related_track = track
                event.type = MessageEventTypes.FAVORITE

        event.save()

        return event

class TrackManager(models.Manager):

    def get_or_create_track(self, data):
        from .models import MxmTrack

        created = False
        try:
            track = MxmTrack.objects.get(commontrack_id=data['commontrack_id'])
        except ObjectDoesNotExist:
            track = self.create_track(data)
            created = True
        return track, created

    def create_track(self, data):
        from .models import MxmTrack

        try:
            track = MxmTrack(
                commontrack_id = data['commontrack_id'],
                artist_name = data['artist_name'],
                track_name = data['track_name'],
                artist_id = data['artist_id'],
                album_id = data['album_id'],
                album_name = data['album_name'],
                track_url = data['track_share_url']
            )

            track.image_url = get_cover_data(
                track.artist_name, track.track_name
            )

            track.vanity_id = data.get('commontrack_vanity_id', 
                " - ".join([track.artist_name, track.track_name])
            )

            track.save()

            return track
        except (ValidationError, KeyError, AttributeError) as e:
            logger.warning("MxmTrack saving error after fetch.")
            raise ValueError("The data doesn't have the form of a track.")

