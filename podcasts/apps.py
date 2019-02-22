from django.apps import AppConfig

class PodcastsConfig(AppConfig):
    name = 'podcasts'
    verbose_name = 'Podcast Manager'

    def ready(self):
        import podcasts.signals
        import pafy
        import os
        from podify.settings import BASE_DIR

        try:
            with open(os.path.join(BASE_DIR, "api-key"), "r") as f:
                api_key = f.readline().strip()
                pafy.set_api_key(api_key)
        except FileNotFoundError as e:
            raise ValueError("You need a file api-key containing the youtube api key")
