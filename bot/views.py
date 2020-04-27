from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import MessageEvent
from .statistics import stats_text
from .musixmatch import track_search
import json
import logging

logger = logging.getLogger(__name__)

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
        except Exception as e:
            logger.exception("MessageEvent creation failed. %s" %str(e))
            return response
        else:
            user = event.sender
            user.send_action('mark_seen')
            user.send_action('typing_on')

        if event.type == MessageEvent.LYRICS:
            mxm = track_search(event.text)

            if mxm.status == 200:
                if mxm.tracks:
                    mxm.tracks = mxm.tracks[:settings.DEFAULT_RECORDS_SIZE]
                    user.send_list_tracks(mxm.tracks)
                else:
                    user.send_text("No encontramos canciones :(")
            else:
                user.send_text("Ups, tuvimos inconvenientes en la búsqueda :o")

        elif event.type == MessageEvent.FAVORITE:
            track = event.related_track
            if user.favorites.filter(commontrack_id=track.commontrack_id).exists():
                user.send_text("*%s* sigue siendo tu favorita :)" % track.track_name)
            else:
                user.favorites.add(track)
                user.send_text("Guardamos *%s* como tu favorita!" % track.track_name)

        elif event.type == MessageEvent.COMMAND:
            if event.text == "/stat":
                msg = stats_text()
            elif event.text == "/fav":
                msg = user.favorites_text()
            else:
                msg = "Prueba con los comandos */stat* o */fav* :D"
            user.send_text(msg)

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
