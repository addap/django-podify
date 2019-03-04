# -*- coding: future_fstrings -*-
import os
import pafy
import requests
import youtube_dl
from datetime import timedelta, datetime
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from time import strptime
import pytz
from django.utils.timezone import make_aware, get_current_timezone_name

from podify.settings import MEDIA_ROOT, BASE_DIR

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
        for episode in self.episode_set.filter(invalid=False, downloaded=False):
            episode.download()
        return f"Downloaded podcast {self}"

    def update_podcast(self):
        """Uses pafy to get all videos in a playlist
        Checks the urls of each episode we have not downloaded yet to see if the video is still available"""

        # if the podcast has a playlist
        if self.playlist_url:
            playlist = pafy.get_playlist2(self.playlist_url)
            # self.name = playlist.title
            # self.slug = slugify(self.name)
            self.description = playlist.description

            # get_playlist2 does not automatically filter out private/deleted videos, for that you have to access at
            # least one of them
            # Afaik it filters out private/deleted videos but keeps videos that are claimed by eg UMG but this
            # is probably because of geo restrictions
            try:
                playlist[0]
            except IndexError:
                pass

            # try to get an image out of it. This still works even with geo restricted videos so I can safely use the
            # first video
            if len(playlist) > 0 and not self.image:
                req = requests.get(playlist[0].thumb)
                self.image.save(f'{self.slug}.jpg', ContentFile(req.content), save=False)

            # add new episodes
            for video in playlist:
                self.episode_set.update_or_create(video_id=video.videoid, defaults={
                    'url': f"{YOUTUBE_BASE}{video.videoid}",
                })

        # iterate over all episodes, even the ones from the playlist, because get_playlist2 in some instances still
        # returns videos that are unavailable
        for episode in self.episode_set.filter(invalid=False):
            try:
                p = pafy.new(episode.url)
            except OSError:
                episode.invalid = True
                episode.save()
                continue

            episode.name = p.title

            if not episode.slug:
                episode.slug = slugify(p.title)
            tz = pytz.timezone(get_current_timezone_name())
            pub_date = datetime(*strptime(p.published, "%Y-%m-%d %H:%M:%S")[:6])
            episode.pub_date = make_aware(pub_date, tz, is_dst=True)
            episode.duration = timedelta(seconds=p.length)
            episode.description = p.description
            episode.video_id = p.videoid
            # check if file exists https://stackoverflow.com/a/41299294
            if episode.mp3:
                exists = bool(episode.mp3.storage.exists(episode.mp3.name))
                if not exists:
                    episode.mp3 = None
                episode.downloaded = exists

            if not episode.image:
                req = requests.get(p.thumb)
                episode.image.save(f'{episode.slug}.jpg', ContentFile(req.content), save=False)
                if not self.image:
                    self.image.save(f'{self.slug}.jpg', episode.image, save=False)

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
    url = models.URLField(blank=True)
    video_id = models.CharField(max_length=11, blank=True, unique=True, null=True)
    mp3 = models.FileField(upload_to='mp3s', blank=True)
    downloaded = models.BooleanField(default=False)
    pub_date = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    invalid = models.BooleanField(default=False)
    image = models.ImageField(upload_to='thumbnails', blank=True)

    # Foreign Key is associated podcast
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def download(self):
        if self.invalid:
            raise ValueError("This episode is invalid. Don't try to download it")

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

        # while True:
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([self.url])
        except youtube_dl.DownloadError as e:
            #todo do something? How can I return errors from admin actions?
            with open("download-error", "w") as f:
                f.write(str(e))
            print(e)
            self.invalid = True
            self.save()
            return

            # Apparently, this caused such a slowdown that everything broke. Firefox stopped trying to load the page
            # and in the end no episode was fully downloaded. I should really look into how to do this asynchronously
            # check mp3 for errors, sometimes they seem to contain errors and podcast addict can't really play them
            #
            # c = subprocess.run(f'ffmpeg -v error -i "{filename}" -f null -'.split(), capture_output=True)
            # if c.stderr == b'':
            #     break
            # else:
            #     #todo log error
            #     pass

        with File(open(filename, "rb")) as f:
            self.mp3.save(f"{self.slug}.mp3", f, save=False)

        os.remove(filename)
        self.downloaded = True
        self.save()

