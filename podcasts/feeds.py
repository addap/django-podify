from django.contrib.syndication.views import Feed
from django.http.request import HttpRequest
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from django_q.tasks import Chain
from datetime import timedelta, datetime
import pytz
from django.utils.timezone import get_current_timezone_name

from .models import Podcast, Episode
from .tasks import podcast_update, podcast_download


class iTunesFeed(Rss201rev2Feed):
    # set content type so that firefox shows me the rss feed in the browser
    content_type = 'application/xml; charset=utf-8'

    def rss_attributes(self):
        attr = super().rss_attributes()
        attr['xmlns:itunes'] = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        return attr

    def add_root_elements(self, handler):
        super().add_root_elements(handler)
        if self.feed['image_url']:
            handler.startElement('image', {})
            handler.addQuickElement('url', self.feed['image_url'])
            handler.addQuickElement('title', f"{self.feed['title']}'s Picture")
            handler.endElement('image')
            handler.startElement('itunes:image', {'href': self.feed['image_url']})
            handler.endElement('itunes:image')

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        handler.addQuickElement('itunes:duration', str(item['duration']))
        if item['image_url']:
            handler.startElement('itunes:image', {'href': item['image_url']})
            handler.endElement('itunes:image')


class RSSEpisode():
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @staticmethod
    def from_episode(e: Episode):
        re = RSSEpisode(
            name=e.name,
            link=reverse('podcasts:episode-download', kwargs={'slug': e.podcast.slug, 'episode_slug': e.slug}),
            mp3_url=e.mp3.url,
            mp3_size=e.mp3.size,
            pub_date=e.pub_date,
            description=e.description,
            image=e.image,
            duration=e.duration,
        )

        return re


class PodcastFeed(Feed):
    feed_type = iTunesFeed
    request = None

    # overwrite __call__ to add cache control header
    def __call__(self, request, *args, **kwargs):
        response = super().__call__(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
        return response

    def get_object(self, request: HttpRequest, **kwargs):
        self.request = request
        return Podcast.objects.get(slug=kwargs['slug'])

    def title(self, podcast: Podcast):
        return podcast.name

    def link(self, podcast: Podcast):
        return reverse('podcasts:podcast-detail', args=(podcast.slug,))

    def feed_url(self, podcast: Podcast):
        return reverse('podcasts:podcast-rss', args=(podcast.slug,))

    def feed_guid(self, podcast: Podcast):
        return podcast.slug

    def description(self, podcast: Podcast):
        return podcast.description

    def feed_extra_kwargs(self, podcast: Podcast):
        image_url = None
        if podcast.image:
            image_url = self.request.build_absolute_uri(podcast.image.url)

        return {'image_url': image_url}

    def items(self, podcast: Podcast):
        dummy_url = reverse('podcasts:dummy-episode-sync', kwargs={'slug': podcast.slug})
        dummy_episode = RSSEpisode(
            name="Sync Podcast",
            link=dummy_url,
            mp3_url=dummy_url,
            mp3_size=0,
            pub_date=datetime.now(tz=pytz.timezone(get_current_timezone_name())),
            description="Trigger a download of this episode to sync the podcast server-side.\nThe download will fail with code 418.\nAfter a while, new episodes will have been downloaded to the server and you can refresh the RSS feed and download them to the phone.",
            image=None,
            duration=timedelta(seconds=0)
        )

        return [dummy_episode] + [RSSEpisode.from_episode(e) for e in podcast.episode_set.filter(downloaded=True)]

    def item_title(self, episode: RSSEpisode):
        return episode.name

    def item_link(self, episode: RSSEpisode):
        return episode.link

    def item_enclosure_url(self, episode: RSSEpisode):
        return self.request.build_absolute_uri(episode.mp3_url)

    def item_enclosure_length(self, episode: RSSEpisode):
        return episode.mp3_size

    def item_enclosure_mime_type(self, item):
        # TODO is this always true? sometimes I download m4a files
        return "audio/mpeg"

    def item_pubdate(self, episode: RSSEpisode):
        return episode.pub_date

    def item_description(self, episode: RSSEpisode):
        return episode.description

    def item_extra_kwargs(self, episode: RSSEpisode):
        image_url = None
        if episode.image:
            image_url = self.request.build_absolute_uri(episode.image.url)

        return {
            'duration': episode.duration,
            'image_url': image_url,
        }
