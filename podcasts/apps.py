from django.apps import AppConfig


class PodcastsConfig(AppConfig):
    name = 'podcasts'
    verbose_name = 'Podcast Manager'

    def ready(self):
        # noinspection PyUnresolvedReferences
        import podcasts.signals
        import pafy
        from podify.settings import env

        api_key = env('API_KEY')
        pafy.set_api_key(api_key)
