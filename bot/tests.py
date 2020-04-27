from django.test import TestCase, Client
from django.urls import reverse
from django.conf import settings
import responses

class WebhookTests(TestCase):

    def setUp(self):
        self.webhook = reverse("webhook-bot")
        self.default_event = {
            'object': 'page',
            'entry': [{'messaging': []}]
        }
        self.payload = {
            "recipient_id": "125447777",
            "message_id": "mid.$cAAa-4cvO"
        }

        responses.add(responses.POST, settings.FB_URL, status=200,json=self.payload)

    def create_message_event(self, messaging):
        """
        Creates a message event given a message object.
        """
        event = {**self.default_event}
        event['entry'][-1]['messaging'].append(messaging)
        return event

    def test_validation(self):
        """
        On a GET request with the appropriate form, the server should return 
        the challenge and a 200 status code.
        """
        challenge = "challenge-string"
        data = {
            'hub.mode': 'subscribe',
            'hub.verify_token': settings.FACEBOOK_VERIFY_TOKEN,
            'hub.challenge': challenge
        }
        c = Client()
        response = c.get(self.webhook, data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.content, 'utf-8'), challenge)

    @responses.activate
    def test_simple_message(self):
        """
        On a very simple small message, the server should at least acknowledge 
        by sending a 200 status code.
        """
        messaging = {
            'sender': {'id': '1331235'},
            'recipient': {'id': '1111111'},
            'message': {'text': 'Hello world.'}
        }
        event = self.create_message_event(messaging)
        c = Client()
        response = c.post(self.webhook, data=event, content_type='application/json')
        self.assertEqual(response.status_code, 200)
