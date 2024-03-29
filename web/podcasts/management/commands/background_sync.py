from django.core.management.base import BaseCommand, CommandError
from django_q.tasks import async_task

from podcasts.models import Podcast
from podcasts.tasks import podcast_update


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--podcast_id', type=int, nargs="+")
        parser.add_argument('--download', action='store_true')

    def handle(self, *args, **options):
        podcast_id = options['podcast_id']
        download = options['download']

        if podcast_id:
            podcast_set = Podcast.objects.filter(pk__in=podcast_id)
        else:
            podcast_set = Podcast.objects.all()

        for podcast in podcast_set:
            try:
                async_task(podcast_update, podcast.pk)
            # except Podcast.DoesNotExist:
            #     raise CommandError(f"Podcast with id {podcast_id} does not exist")
            except ValueError as err:
                raise CommandError(err)
