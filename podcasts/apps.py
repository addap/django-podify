from django.apps import AppConfig


class PodcastsConfig(AppConfig):
    name = 'podcasts'
    verbose_name = 'Podcast Manager'

    def ready(self):
        # import signal connections
        import podcasts.signals
