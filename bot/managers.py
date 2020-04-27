from django.db import models
from django.utils.timezone import now
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.conf import settings
from .spotify import get_cover_data
from .choices import MessageEventTypes

def save_user_session(sender):
    from .models import UserSession

    is_new_session = True
    sessions = UserSession.objects.filter(user__id=sender.id)

    if sessions.exists():
        last_session = sessions.order_by('end_time').last()
        if now() - last_session.end_time <= settings.SESSION_TIME_THRESHOLD:
            is_new_session = False
            last_session.save()

    if is_new_session:
        UserSession.objects.create(user=sender)

class MessageManager(models.Manager):

    def create_message(self, query):
        from .models import BotUser, MessageEvent, MxmTrack

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
        save_user_session(sender)

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

            event.text=message_text
            event.type=event_type

        elif hook_type == settings.POSTBACK_HOOK:
            commontrack_id = hook_payload['payload']
            try:
                track = MxmTrack.objects.get(commontrack_id=commontrack_id)
            except ObjectDoesNotExist as e:
                print(e)
                raise ValueError
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
            commontrack_id = data['commontrack_id']
            artist_name = data['artist_name']
            track_name = data['track_name']
            artist_id = data['artist_id']
            album_id = data['album_id']
            album_name = data['album_name']
            track_url = data['track_share_url']
            try:
                vanity_id = data['commontrack_vanity_id']
            except KeyError:
                vanity_id = artist_name + " - " + track_name

            cover_url = get_cover_data(artist_name, track_name)

            track = MxmTrack(
                commontrack_id=commontrack_id,
                artist_name=artist_name,
                track_name=track_name,
                artist_id=artist_id,
                album_id=album_id,
                image_url=cover_url,
                track_url=track_url,
                album_name=album_name,
                vanity_id=vanity_id
            )
            track.save()
            return track
        except (ValidationError, KeyError, AttributeError) as e:
            print(e)
            raise ValueError("The data doesn't have the form of a track.")

