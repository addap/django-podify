# -*- coding: future_fstrings -*-
import os
import pafy
import requests
import youtube_dl
from datetime import timedelta, datetime
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
import subprocess
from django.utils.text import slugify

from podify.settings import MEDIA_ROOT

YOUTUBE_BASE = 'https://www.youtube.com/watch?v='


# Create your models here.
class Podcast(models.Model):
    """Model for a podcast
        name : the name of the podcast
        url  : the playlist's url if applicable
        slug : a url friendly version of the name"""

    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    playlist_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='thumbnails', blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """When a podcast is saved for the first time we get the episode urls."""
        first_save = False
        if self._state.adding:
            first_save = True
            self.slug = slugify(self.name)
        super().save(*args, **kwargs) # we have to save once so that we can .create() Episodes when syncing
        if first_save:
            self.update_podcast()
            super().save(*args, **kwargs) # save again so now that we have the image

    def __str__(self):
        return self.name

    def download_podcast(self):
        self.update_podcast()
        for episode in self.episode_set.filter(invalid=False):
            episode.download()
        return f"Downloaded podcast {self}"

    def update_podcast(self):
        """Uses pafy to get all videos in a playlist
        Checks the urls of each episode we have not downloaded yet to see if the video is still available"""

        # if the podcast has a playlist
        if self.url:
            playlist = pafy.get_playlist2(self.url)
            # self.name = playlist.title
            # self.slug = slugify(self.name)
            self.description = playlist.description

            # get_playlist2 does not automatically filter out private/deleted videos, for that you have to access at least on of them
            try:
                playlist[0]
            except IndexError:
                pass

            # try to get an image out of it
            if len(playlist) > 0 and not self.image:
                req = requests.get(playlist[0].thumb)
                self.image.save(f'{self.slug}.jpg', ContentFile(req.content))

            # add new episodes
            for video in playlist:
                self.episode_set.update_or_create(video_id=video.videoid, defaults={
                    'name': video.title,
                    'slug': slugify(video.title),
                    'url': f"{YOUTUBE_BASE}{video.videoid}",
                    'pub_date': datetime.fromisoformat(video.published),
                    'duration': timedelta(seconds=video.length),
                    'video_id': video.videoid,
                    'description': video.description,
                    'playlist_episode': True,
                })

        # the podcast's episodes that are not from the playlist
        for episode in self.episode_set.filter(playlist_episode=False, invalid=False):
            try:
                p = pafy.new(episode.url)
            except OSError:
                episode.invalid = True
                episode.save()
                continue

            if not self.image:
                req = requests.get(p.thumb)
                self.image.save(f'{self.slug}.jpg', ContentFile(req.content))

            episode.name = p.title
            episode.slug = slugify(p.title)
            episode.pub_date = datetime.fromisoformat(p.published)
            episode.duration = timedelta(seconds=p.length)
            episode.description = p.description
            episode.video_id = p.videoid
            episode.save()

        return f"Updated podcast {self}"


class Episode(models.Model):
    """Model for a podcast episode
        name: name of the episode
        url: url of the audio file from where to download it
        downloaded: boolean whether we have downloaded the file to the server
        mp3: the location of the mp3 file on the server
    """
    name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    url = models.URLField()
    video_id = models.CharField(max_length=11, blank=True, unique=True)
    mp3 = models.FileField(upload_to='mp3s', blank=True)
    downloaded = models.BooleanField(default=False)
    pub_date = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    invalid = models.BooleanField(default=False)
    playlist_episode = models.BooleanField(default=False)

    # Foreign Key is associated podcast
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def download(self):
        filename = f'{MEDIA_ROOT}{self.slug}.mp3'
        ydl_opts = {
            'format': 'bestaudio[ext!=webm]/best[ext!=webm]/[ext!=webm]',
            'outtmpl': filename,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
        }

        while True:
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([self.url])
            except youtube_dl.DownloadError as e:
                #todo do something? How can I return errors from admin actions?
                self.invalid = True
                self.save()
                return

            # check mp3 for errors, sometimes they seem to contain errors and podcast addict can't really play them
            # todo It wasn't because of errors but because podcast addict cannot play webm encoded files that well.
            # still, leaving it in for some time and todo log if there is an error
            c = subprocess.run(f'ffmpeg -v error -i "{filename}" -f null -'.split(), capture_output=True)
            if c.stderr == b'':
                break
            else:
                #todo log error
                pass

        with File(open(filename, "rb")) as f:
            self.mp3.save(f"{self.slug}.mp3", f)

        os.remove(filename)
        self.downloaded = True
        self.save()

