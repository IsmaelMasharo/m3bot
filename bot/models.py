from django.db import models
from .managers import MessageManager 
import datetime

# Create your models here.
class BotUser(models.Model):
    """
    """
    psid = models.TextField(unique=True)


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
    # Possible types of messages
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

    # Custom manager
    objects = MessageManager()

    def __str__(self):
        return self.text

