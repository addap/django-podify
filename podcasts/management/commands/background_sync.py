from django.core.management.base import BaseCommand, CommandError
from podcasts.models import Podcast


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument('--podcast_id', type=int, nargs="+")

    def handle(self, *args, **options):
        podcast_id = options['podcast_id']
        if podcast_id:
            try:
                podcast = Podcast.objects.get(pk=podcast_id)
                self.stdout.write(podcast.sync_podcast())
                podcast.save()
            except Podcast.DoesNotExist:
                raise CommandError(f"Podcast with id {podcast_id} does not exist")
            except ValueError as err:
                raise CommandError(f"{err}")
        else:
            for podcast in Podcast.objects.all():
                try:
                    self.stdout.write(podcast.sync_podcast())
                    podcast.save()
                except ValueError as err:
                    raise CommandError(f"{err}")

