import os

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from podify.settings import MEDIA_ROOT

from podcasts.models import Podcast
from podcasts.tasks import podcast_update, podcast_download


class Command(BaseCommand):
    # def add_arguments(self, parser):
    #     parser.add_argument('--podcast_id', type=int, nargs="+")
    #     parser.add_argument('--download', action='store_true')

    def handle(self, *args, **options):
        # go through the media directory and scan for directories containing a .makepodcast file
        # then create a podcast from that and episodes from all the audio files within
        # the assumption is that these directories only contain a single .makepodcast file and the rest is audio files
        media, media_dirs, _ = next(os.walk(MEDIA_ROOT))
        for media_dir in media_dirs:
            root, _, media_files = next(os.walk(os.path.join(media, media_dir)))
            if '.makepodcast' in media_files:
                media_files.remove('.makepodcast')

                print(f"making a podcast out of {root}")
                # create podcast
                p = Podcast.objects.create(name=media_dir, slug=slugify(media_dir))
                if '.description' in media_files:
                    with open(os.path.join(root, ".description"), "r") as desc:
                        p.description = desc.read()
                    media_files.remove('.description') 

                if 'image.jpg' in media_files:
                    p.image = os.path.join(media_dir, 'image.jpg')
                    media_files.remove('image.jpg')

                # add all episodes
                for media_file in media_files:
                    p.add_episode_file(os.path.join(root, media_file))
                p.save()
                os.remove(os.path.join(root, '.makepodcast'))
