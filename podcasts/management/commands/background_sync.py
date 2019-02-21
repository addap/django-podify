# -*- coding: future_fstrings -*-
from django.core.management.base import BaseCommand, CommandError
from podcasts.models import Podcast


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--podcast_id', type=int, nargs="+")

    def handle(self, *args, **options):
        podcast_id = options['podcast_id']
        if podcast_id:
            podcast_set = Podcast.objects.filter(pk__in=podcast_id)
        else:
            podcast_set = Podcast.objects.all()

        for podcast in podcast_set:
            try:
                self.stdout.write(podcast.download_podcast())
            except Podcast.DoesNotExist:
                raise CommandError(f"Podcast with id {podcast_id} does not exist")
            except ValueError as err:
                raise CommandError(err)
            podcast.save()

