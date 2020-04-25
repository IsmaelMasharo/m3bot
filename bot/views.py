from django.http import HttpResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

import json

# from .models import MessageEvent, stats_text
# from .musixmatch import track_search
# import json, sys, traceback


@csrf_exempt
def webhook_messenger(request: HttpRequest):
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
        # Responding to a Messenger API request.
        query = json.loads(request.body)
        print(query)
        return response


    elif request.method == 'GET':
        # Facebook uses a GET for subscription to the webhook.

        # Hard-coded token for verification used by Facebook.
        verify_token = settings.VERIFY_TOKEN
        # Contents of the GET request.
        query = request.GET

        # We now verify the request has the appropriate form.
        if 'hub.mode' in query and 'hub.verify_token' in query:
            mode = query['hub.mode']
            token = query['hub.verify_token']
            challenge = query.get('hub.challenge')

            # Check the mode of the query is subscribe, and whether the token matches.
            if mode == 'subscribe' and token == verify_token:
                # The token matched! Send the challenge back to verify.
                response.content = challenge
                response.status_code = 200
            else:
                # Forbidden: The token didn't match.
                response.status_code = 403

    return response
