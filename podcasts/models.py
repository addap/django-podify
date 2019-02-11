from django.db import models


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
    slug = models.CharField(max_length=40)
    name = models.CharField(max_length=40)
    podcast_type = models.CharField(max_length=3, choices=PODCAST_TYPE_CHOICES, default=YOUTUBE_PLAYLIST)
    url = models.URLField()

    def __save__(self, *args, **kwargs):
        """When a podcast is saved for the first time we get the episode urls."""
        if self._state.adding is True:
            self.sync_podcast()
        super().save(*args, **kwargs)

    def sync_podcast(self):
        if self.podcast_type == Podcast.YOUTUBE_PLAYLIST:
            return self.sync_yt_playlist()
        elif self.podcast_type == Podcast.SINGLES:
            return self.sync_yt_singles()

    def sync_yt_playlist(self):
        """Uses the YouTube api to get all videos in a playlist"""
        return f"Synced {self}"

    def sync_yt_singles(self):
        # todo check if videos are still available
        return f"Synced {self}"


class Episode(models.Model):
    name = models.CharField(max_length=40)
    url  = models.URLField()
    downloaded = models.BooleanField(default=False)
    mp3_file = models.URLField()
    
    # Foreign Key is associated podcast
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)

