from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Assignment, Notification

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@receiver(post_save, sender=Assignment)
def notify_new_assignment(sender, instance, created, **kwargs):
    if created:
        students = User.objects.filter(student__isnull=False)
        for student in students:
            note = Notification.objects.create(
                user=student,
                message=f"New assignment posted: {instance.title}",
                url=f"/assignments/{instance.id}/"
            )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{student.id}",
                {
                    'type': 'send_notification',
                    'message': note.message,
                    'url': note.url,
                }
            )
