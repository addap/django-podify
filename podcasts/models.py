import os
from datetime import timedelta, datetime
from io import BytesIO
from time import strptime

import mutagen.id3
import mutagen.mp3
import pafy
import pytz
import requests
import youtube_dl
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from django.utils.timezone import make_aware, get_current_timezone_name
from django_q.tasks import async_task

from podify.settings import MEDIA_ROOT
from .tasks import episode_download



def podcast_media_path(instance, filename):
    return f'{instance.slug}/{filename}'


# Create your models here.
class Podcast(models.Model):
    """Model for a podcast
        name : the name of the podcast
        url  : the playlist's url if applicable
        slug : a url friendly version of the name

        The data for a podcast is saved in MEDIA_ROOT/<slug>"""

    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    playlist_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=podcast_media_path, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """When a podcast is saved for the first time we update once to get the episode urls."""
        if self._state.adding:
            self.slug = slugify(self.name)
            os.makedirs(os.path.join(MEDIA_ROOT, self.slug), exist_ok=True)
        super().save(*args, **kwargs)  # we have to save once so that we can .create() Episodes when syncing

    def __str__(self):
        return self.name

    def add_episode_mp3(self, mp3):
        name = mp3.name
        slug = slugify(name)
        pub_date = datetime.now(tz=pytz.timezone(get_current_timezone_name()))
        audio = mutagen.mp3.MP3(mp3, ID3=mutagen.id3.ID3)
        duration = timedelta(seconds=audio.info.length)
        # save thumbnail separately
        try:
            b = audio.tags.getall('APIC')[0].data
            image = File(BytesIO(b), name=f'{name}-thumbnail')
        except:
            image = None

        self.episode_set.create(
            name=name,
            slug=slug,
            mp3=mp3,
            pub_date=pub_date,
            image=image,
            duration=duration,
            downloaded=True,
            updated=True)

    def update(self):
        """Uses pafy to create episodes from all videos in a playlist."""
        # add all videos from playlist
        if self.playlist_url:
            playlist = pafy.get_playlist2(self.playlist_url)
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
                if not self.episode_set.filter(url=video.watchv_url).exists():
                    self.episode_set.create(url=video.watchv_url)

        self.save()

        # how would I throw that into the queue aswell? I could create a group and block unit that's done
        for episode in self.episode_set.filter(invalid=False, updated=False):
            episode.update()

        return f"Updated podcast {self}"

    def download(self):
        for episode in self.episode_set.filter(invalid=False, downloaded=False):
            async_task(episode_download, episode.pk)

        return f"Downloaded podcast {self}"


def episode_media_path(instance, filename):
    return f'{instance.podcast.slug}/{filename}'


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
    video_id = models.CharField(max_length=11, blank=True, null=True)
    mp3 = models.FileField(upload_to=episode_media_path, blank=True)
    downloaded = models.BooleanField(default=False)
    updated = models.BooleanField(default=False)
    pub_date = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    invalid = models.BooleanField(default=False)
    image = models.ImageField(upload_to=episode_media_path, blank=True)

    # Foreign Key is associated podcast
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def update(self):
        if not self.url:
            print(f'episode {self.id} does not have a URL.')
            return

        try:
            p = pafy.new(self.url)
        except OSError:
            self.invalid = True
            self.save()
            return

        self.name = p.title
        self.slug = slugify(p.title)
        print(self.slug)
        tz = pytz.timezone(get_current_timezone_name())
        pub_date = datetime(*strptime(p.published, "%Y-%m-%d %H:%M:%S")[:6])
        self.pub_date = make_aware(pub_date, tz, is_dst=True)
        self.duration = timedelta(seconds=p.length)
        self.description = p.description

        # check if file still exists https://stackoverflow.com/a/41299294
        if self.mp3:
            exists = bool(self.mp3.storage.exists(self.mp3.name))
            if not exists:
                self.mp3 = None
            self.downloaded = exists

        req = requests.get(p.thumb)
        self.image.save(f'{self.slug}.jpg', ContentFile(req.content), save=False)

        self.updated = True
        self.save()
        return f'Episode {self.url} ({self.id}) updated successfully'

    def download(self):
        if self.invalid:
            raise ValueError("This episode is invalid. Don't try to download it")

        filename_relative = os.path.join(self.podcast.slug, f'{self.slug}.mp3')
        filename = os.path.join(MEDIA_ROOT, filename_relative)
        ydl_opts = {
            'format': 'bestaudio[ext!=webm]/best[ext!=webm]/[ext!=webm]',
            'outtmpl': filename,
            'quiet': True,
            'embed-thumbnail': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                # todo maybe download all episodes at the same time
                ydl.download([self.url])
        except youtube_dl.DownloadError as e:
            # todo log properly
            with open("download-error", "w") as f:
                f.write(str(e))
            print(e)
            self.invalid = True
            self.save()
            return

        self.mp3 = filename_relative
        self.downloaded = True
        self.save()
        return f'Episode {self.url} ({self.id}) downloaded successfully '
