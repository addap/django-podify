import os
import os.path
from datetime import timedelta, datetime
from time import strptime
from io import BytesIO
from PIL import Image

import mutagen.id3
import mutagen.mp3

import requests
import yt_dlp
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from django.utils.text import slugify
from django.utils import timezone
from django.utils.crypto import get_random_string
from django_q.tasks import async_task, delete_group
from .ytdl import get_episode_info, get_playlist_info

from podify.settings import MEDIA_ROOT
from .tasks import episode_update


def podcast_media_path(instance, filename):
    return os.path.join(instance.slug, filename)


def audio_file_extract_info(mp3):
    try:
        audio = mutagen.mp3.MP3(mp3, ID3=mutagen.id3.ID3)
        duration = timedelta(seconds=audio.info.length)
    except:
        duration = timedelta(seconds=0)

    # save thumbnail separately
    try:
        b = audio.tags.getall('APIC')[0].data
        image = File(BytesIO(b), name=f'{name}-thumbnail')
    except:
        image = None

    return (duration, image)


class Podcast(models.Model):
    """Model for a podcast
The data for a podcast is saved in MEDIA_ROOT/<slug>"""

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    playlist_url = models.URLField(blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=podcast_media_path, blank=True)
    pub_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def add_episode_file(self, filepath):
        (tmp, ext) = os.path.splitext(filepath)
        pathname = os.path.dirname(tmp)
        filename = os.path.basename(tmp)

        slug = f'{slugify(filename)}-{get_random_string(10)}'
        mp3name = slug + ext
        os.rename(filepath, os.path.join(pathname, mp3name))
        pub_date = timezone.now()
        with open(os.path.join(pathname, mp3name), "rb") as f:
            audio = mutagen.mp3.MP3(f, ID3=mutagen.id3.ID3)
            duration = timedelta(seconds=audio.info.length)
            # save thumbnail separately
            try:
                b = audio.tags.getall('APIC')[0].data
                image = File(BytesIO(b), name=f'{filename}-thumbnail')
            except:
                image = None

        self.episode_set.create(
            name=filename,
            mp3=os.path.join(os.path.basename(pathname), mp3name),
            slug=slug,
            pub_date=pub_date,
            image=image,
            duration=duration,
            # todo change to initialized
            downloaded=True,
            updated=True)

    def add_episode_upload_mp3(self, mp3):
        (name, ext) = os.path.splitext(mp3.name)
        slug = f'{slugify(name)}-{get_random_string(10)}'
        mp3.name = slug + ext
        pub_date = timezone.now()

        (duration, image) = audio_file_extract_info(mp3)

        self.episode_set.create(
            name=name,
            slug=slug,
            mp3=mp3,
            pub_date=pub_date,
            image=image,
            duration=duration,
            initialized=True)

    def update(self):
        """Collect all episodes that we should have and update them in turn."""
        if not self.playlist_url:
            return

        info = get_playlist_info(self.playlist_url)

        self.description = info['description']
        for episode_info in info['entries']:
            if self.episode_set.filter(url=episode_info['url']).exists():
                continue
            self.episode_set.create(url=episode_info['url'])

        delete_group(self.slug, tasks=True)
        for episode in self.episode_set.filter(invalid=False, initialized=False):
            async_task(episode_update, episode.pk, group=self.slug)

        self.save()
        return f"Updated podcast {self}"


def episode_media_path(instance, filename):
    return os.path.join(instance.podcast.slug, filename)


class Episode(models.Model):
    """Model for a podcast episode. Each podcast is composed of episodes, which are shown in the RSS feed if they are initialized."""
    name = models.CharField(max_length=100, blank=True)
    slug = models.SlugField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    mp3 = models.FileField(upload_to=episode_media_path, blank=True)
    pub_date = models.DateTimeField(blank=True, null=True)
    duration = models.DurationField(blank=True, null=True)
    image = models.ImageField(upload_to=episode_media_path, blank=True)

    # only relevant if downloaded from YT
    url = models.URLField(blank=True)
    video_id = models.CharField(max_length=11, blank=True, null=True)

    invalid = models.BooleanField(
        default=False, help_text='Whether there was an error with the episode. The episode will be disregarded in future operations.')
    initialized = models.BooleanField(
        default=False, help_text='Whether the episode metadata & mp3 are present.')

    # Foreign Key is associated podcast
    podcast = models.ForeignKey(Podcast, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    @property
    def downloaded(self):
        """Check if file still exists https://stackoverflow.com/a/41299294"""
        if not self.invalid and self.mp3:
            exists = bool(self.mp3.storage.exists(self.mp3.name))
            if not exists:
                self.mp3 = None
            return exists
        else:
            return False

    def update(self):
        if not self.url:
            print(f'Episode {self.id} does not have a URL.')
            return
        if self.invalid:
            print(f'Episode {self.id} is invalid.')
            return
        if self.initialized:
            print(
                f'Episode {self.id} is already initialized {self.initialized}.')
            return

        info = get_episode_info(self.url)

        if not self.name:
            self.name = info['title']
        self.slug = f'{slugify(self.name)}-{get_random_string(10)}'
        self.description = info['description']

        tz = timezone.get_current_timezone()
        self.pub_date = datetime(
            *strptime(info['upload_date'], "%Y%m%d")[0:6], tzinfo=tz)
        self.duration = timedelta(seconds=int(info['duration']))

        r = requests.get(info['thumbnail'])
        # TODO better way to convert to JPG?
        thumb = ContentFile(r.content)
        img = Image.open(thumb)
        thumb_jpg = BytesIO()
        img.save(thumb_jpg, format="jpeg")
        self.image.save(f'{self.slug}.jpg', thumb_jpg, save=False)

        # also set the podcast's image every time I add a new episode. This will probably set it nondeterministically if I
        # add multiple episodes but I don't care since I just want any picture
        if self.podcast.image:
            self.podcast.image.delete(save=False)
        self.podcast.image.save(f'{self.podcast.slug}.jpg', thumb_jpg)

        # download mp3
        filename_relative = episode_media_path(self, f'{self.slug}.m4a')
        filename = os.path.join(MEDIA_ROOT, filename_relative)
        ydl_opts = {
            'format': 'm4a/bestaudio[ext!=webm]/best[ext!=webm]/[ext!=webm]',
            'outtmpl': filename,
            'quiet': True,
            'embed-thumbnail': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredquality': '128',
                'preferredcodec': 'm4a'
            }],
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(self.url)
        except yt_dlp.DownloadError as e:
            # todo log properly
            with open("download-error", "w") as f:
                f.write(str(e))
            print(e)
            self.invalid = True
            self.save()
            return

        self.mp3 = filename
        self.initialized = True

        self.save()
        return f'Episode {self.url} ({self.id}) updated successfully '
