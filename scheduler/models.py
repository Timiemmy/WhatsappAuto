from django.db import models
from django.contrib.auth.models import User

class ScheduledMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15)
    message = models.TextField()
    send_hour = models.IntegerField()
    send_minute = models.IntegerField()
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Message to {self.phone_number} at {self.send_hour}:{self.send_minute}"

    @classmethod
    def total_scheduled(cls, user=None):
        """Get total messages scheduled (optionally filtered by user)"""
        if user:
            return cls.objects.filter(user=user).count()
        return cls.objects.count()

    @classmethod
    def total_sent(cls, user=None):
        """Get total messages sent (optionally filtered by user)"""
        if user:
            return cls.objects.filter(user=user, sent=True).count()
        return cls.objects.filter(sent=True).count()
