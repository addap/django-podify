from django.db import models
from django.core.files.base import ContentFile
from datetime import timedelta, datetime
from pafy import get_playlist2
import requests

YOUTUBE_BASE = 'https://www.youtube.com/watch?v='


# Create your models here.
class Podcast(models.Model):
    """Model for a podcast. The different types are
        - Youtube playlist: a playlist of videos
        - Singles         : individual videos, the urls have to be supplied by the user

        name : the name of the podcast
        url  : the playlist's url if applicable
        slug : a url friendly version of the name"""

    YOUTUBE_PLAYLIST = 'YTP'
    SINGLES = 'SNG'
    PODCAST_TYPE_CHOICES = (
        (YOUTUBE_PLAYLIST, 'YouTube Playlist'),
        (SINGLES, 'Single Videos'),
    )

    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    podcast_type = models.CharField(max_length=3, choices=PODCAST_TYPE_CHOICES, default=YOUTUBE_PLAYLIST)
    url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='thumbnails', blank=True)

    def save(self, *args, **kwargs):
        """When a podcast is saved for the first time we get the episode urls."""
        first_save = False
        if self._state.adding is True:
            first_save = True
        super().save(*args, **kwargs) # we have to save once so that we can .create Episodes when syncing
        if first_save:
            self.sync_podcast()
        super().save(*args, **kwargs) # save again so now that we have the image

    def __str__(self):
        return self.name

    def sync_podcast(self):
        if self.podcast_type == Podcast.YOUTUBE_PLAYLIST:
            return self.sync_yt_playlist()
        elif self.podcast_type == Podcast.SINGLES:
            return self.sync_yt_singles()

    def sync_yt_playlist(self):
        """Uses the YouTube api to get all videos in a playlist"""
        if not self.url:
            raise ValueError("A Youtube playlist needs a url")
        playlist = get_playlist2(self.url)
        # self.name = playlist.title
        # self.slug = slugify(self.name)
        self.description = playlist.description

        # try to get an image out of it
        if len(playlist) > 0:
            req = requests.get(playlist[0].thumb, stream=True)
            self.image.save(f'{self.slug}.jpg', ContentFile(req.content))

        # delete old episodes
        for episode in self.episode_set.all():
            episode.delete()
        # add new episodes
        for video in playlist:
            # todo what happens to videos longer than 24 hours?
            self.episode_set.create(name=video.title,
                                    url=f"{YOUTUBE_BASE}{video.videoid}",
                                    pub_date=datetime.fromisoformat(video.published),
                                    duration=timedelta(seconds=video.length))

    def sync_yt_singles(self):
        # todo check if videos are still available
        return f"Synced {self}"


class Episode(models.Model):
    """Model for a podcast episode
        name: name of the episode
        url: url of the audio file from where to download it
        downloaded: boolean whether we have downloaded the file to the server
        mp3: the location of the mp3 file on the server
    """
    name = models.CharField(max_length=100)
    url = models.URLField()
    downloaded = models.BooleanField(default=False)
    mp3 = models.FileField(upload_to=None, blank=True)
    pub_date = models.DateTimeField(default=datetime.now)
    duration = models.DurationField(default=timedelta())
    
    # Foreign Key is associated podcast
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

