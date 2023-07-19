from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class PodcastsConfig(AppConfig):
    name = 'podcasts'
    verbose_name = 'Podcast Manager'

    def ready(self):
        # import signal connections
        import podcasts.signals
        logger.info("Starting Podify")
