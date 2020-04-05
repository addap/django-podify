import os
import shutil

from django.db.models.signals import pre_delete
from django.dispatch import receiver
from django_q.signals import pre_enqueue, pre_execute

from podcasts.models import Podcast, Episode
from podify.settings import MEDIA_ROOT


@receiver(pre_delete, sender=Podcast, dispatch_uid="deleting podcast files")
def podcast_delete_files(sender, **kwargs):
    podcast = kwargs['instance']
    # remote everything from that podcast, the episode signals will then do nothing
    shutil.rmtree(os.path.join(MEDIA_ROOT, podcast.slug))


@receiver(pre_delete, sender=Episode, dispatch_uid="deleting episode files")
def episode_delete_files(sender, **kwargs):
    episode = kwargs['instance']
    if episode.mp3 and episode.mp3.storage.exists(episode.mp3.name):
        os.remove(episode.mp3.path)
    if episode.image and episode.image.storage.exists(episode.image.name):
        os.remove(episode.image.path)


@receiver(pre_enqueue)
def my_pre_enqueue_callback(sender, task, **kwargs):
    print("Task {} will be enqueued".format(task["name"]))


@receiver(pre_execute)
def my_pre_execute_callback(sender, func, task, **kwargs):
    print("Task {} will be executed by calling {}".format(
        task["name"], func))
