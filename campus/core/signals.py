from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Assignment, Notification

@receiver(post_save, sender=Assignment)
def notify_new_assignment(sender, instance, created, **kwargs):
    if created:
        print(f"Signal fired: New assignment created: {instance.title}")
        students = User.objects.filter(student__isnull=False)
        for student in students:
            Notification.objects.create(
                user=student,
                message=f"New assignment posted: {instance.title}"
            )
        print(f"Notifications created for {students.count()} students.")
