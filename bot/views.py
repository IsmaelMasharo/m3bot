from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import MessageEvent
import json

from .musixmatch import track_search
# import json, sys, traceback


@csrf_exempt
def webhook_messenger(request):
    """
    View that interacts with the Facebook Messenger API.

    A GET method is used to subscribe to the webhook, and POST is used for actual API interaction.
    It is required that the server returns a 200 status code on every request.

    :param request: HttpRequest sent to the server.
    :return: HttpResponse that acknowledges the interaction in case it's well-formed according to
        the API standards.
    """
    response = HttpResponse(status=200, content_type='application/json')
    response.content = 'OK'

    if request.method == 'POST':
        query = json.loads(request.body)

        try:
            event = MessageEvent.objects.create_message(query)
        except ValueError as e:
            print(e)
            return response
        else:
            user = event.sender
            # Mark that we've seen the message
            user.send_action('mark_seen')
            # Signal that we are writing a message
            user.send_action('typing_on')

        if event.type == MessageEvent.LYRICS:
            mxm = track_search(event.text)

            if mxm.status == 200:
                if mxm.tracks:
                    mxm.tracks = mxm.tracks[:settings.DEFAULT_RECORDS_SIZE]
                    user.send_list_tracks(mxm.tracks)
                else:
                    user.send_text("Couldn't find lyrics.")
            else:
                user.send_text("Couldn't contact the lyrics service.")

        return response


    elif request.method == 'GET':
        verify_token = settings.VERIFY_TOKEN
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
