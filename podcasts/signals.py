import os
import shutil

from django.db.models.signals import pre_delete, pre_save
from django.dispatch import receiver
from django_q.signals import pre_enqueue, pre_execute

from podcasts.models import Podcast, Episode
from podify.settings import MEDIA_ROOT


@receiver(pre_save, sender=Podcast, dispatch_uid="creating podcast dir")
def podcast_create_dir(sender, instance, **kwargs):
    os.makedirs(os.path.join(MEDIA_ROOT, instance.slug), exist_ok=True)


@receiver(pre_delete, sender=Podcast, dispatch_uid="deleting podcast files")
def podcast_delete_files(sender, instance, **kwargs):
    print(f'Podcast {instance.name} will be deleted')
    # remote everything from that podcast, the episode signals will then do nothing
    shutil.rmtree(os.path.join(MEDIA_ROOT, instance.slug))


@receiver(pre_delete, sender=Episode, dispatch_uid="deleting episode files")
def episode_delete_files(sender, instance, **kwargs):
    print(f'Episode {instance.name} will be deleted')
    if instance.mp3 and instance.mp3.storage.exists(instance.mp3.name):
        os.remove(instance.mp3.path)
    if instance.image and instance.image.storage.exists(instance.image.name):
        os.remove(instance.image.path)


@receiver(pre_enqueue)
def my_pre_enqueue_callback(sender, task, **kwargs):
    print(f'Task {task["name"]} will be enqueued')


@receiver(pre_execute)
def my_pre_execute_callback(sender, func, task, **kwargs):
    print(f'Task {task["name"]} will be executed by calling {func}')
