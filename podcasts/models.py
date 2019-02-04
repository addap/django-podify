from django.db import models

# Create your models here.
class Podcast(models.Model):
    YOUTUBE_PLAYLIST = 'YTP'
    SINGLES = 'SNG'
    PODCAST_TYPE_CHOICES = (
        (YOUTUBE_PLAYLIST, 'YouTube Playlist'),
        (SINGLES, 'Single Videos'),
    )
    title = models.CharField(max_length=40)
    name = models.CharField(max_length=40)
    podcast_type = models.CharField(max_length=3, choices=PODCAST_TYPE_CHOICES, default=YOUTUBE_PLAYLIST)
    url  = models.URLField()

class Episode(models.Model):
    name = models.CharField(max_length=40)
    url  = models.URLField()
    downloaded = models.BooleanField(default=False)
    mp3_file = models.URLField()
    
    # Foreign Key is associated podcast
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)
    
