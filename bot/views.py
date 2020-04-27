from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import MessageEvent
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def webhook_messenger(request):
    """
    GET: Subscribe to the webhook
    POST: API interaction.
    """
    response = HttpResponse(status=200, content_type='application/json')
    response.content = 'OK'

    if request.method == 'POST':
        query = json.loads(request.body)

        try:
            event = MessageEvent.objects.create_message(query)
        except Exception as e:
            logger.exception("MessageEvent creation failed. %s" %str(e))
            return response

        event.sender.send_action('mark_seen')
        event.sender.send_action('typing_on')
        event.handle_event()

        return response

    elif request.method == 'GET':
        verify_token = settings.FACEBOOK_VERIFY_TOKEN
        query = request.GET

        if 'hub.mode' in query and 'hub.verify_token' in query:
            mode = query['hub.mode']
            token = query['hub.verify_token']
            challenge = query.get('hub.challenge')

            if mode == 'subscribe' and token == verify_token:
                response.content = challenge
                response.status_code = 200
            else:
                response.status_code = 403

    return response
