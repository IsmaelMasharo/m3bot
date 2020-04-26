from django.db import models
from django.utils.timezone import now
from django.conf import settings

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
        from .models import BotUser, MessageEvent

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

            event_type = MessageEvent.LYRICS
            if (
                message_text[settings.COMMAND_INDEX_AT] == \
                settings.COMMAND_IDENTIFIER
            ):
                event_type = MessageEvent.COMMAND

            event.text=message_text
            event.type=event_type

        elif hook_type == settings.POSTBACK_HOOK:
            pass

        event.save()

        return event
