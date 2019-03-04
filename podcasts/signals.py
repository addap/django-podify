import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from podcasts.models import Podcast, Episode


@receiver(pre_delete, sender=Podcast, dispatch_uid="deleting podcast files")
def podcast_delete_files(sender, **kwargs):
    podcast = kwargs['instance']
    if podcast.image and podcast.image.storage.exists(podcast.image.name):
        os.remove(podcast.image.path)


@receiver(pre_delete, sender=Episode, dispatch_uid="deleting episode files")
def episode_delete_files(sender, **kwargs):
    episode = kwargs['instance']
    if episode.mp3 and episode.mp3.storage.exists(episode.mp3.name):
        os.remove(episode.mp3.path)
    if episode.image and episode.image.storage.exists(episode.image.name):
        os.remove(episode.image.path)
