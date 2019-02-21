from django.apps import AppConfig


class PodcastsConfig(AppConfig):
    name = 'podcasts'
    verbose_name = 'Podcast Manager'

    def ready(self):
        import podcasts.signals
        import pafy

        try:
            with open("api-key") as f:
                api_key = f.readline()
                pafy.set_api_key(api_key)
        except FileNotFoundError as e:
            raise ValueError("You need a file api-key containing the youtube api key")
