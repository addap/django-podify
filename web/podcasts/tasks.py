import podcasts.models


def podcast_update(podcast_id):
    podcast = podcasts.models.Podcast.objects.get(pk=podcast_id)
    podcast.update()


def episode_update(episode_id):
    episode = podcasts.models.Episode.objects.get(pk=episode_id)
    episode.update()
