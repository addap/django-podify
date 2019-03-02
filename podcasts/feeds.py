# -*- coding: future_fstrings -*-
from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed
from django.http.request import HttpRequest

from .models import Podcast, Episode


class iTunesFeed(Rss201rev2Feed):
    # set content type so that firefox shows me the rss feed in the browser
    content_type = 'application/xml; charset=utf-8'

    def rss_attributes(self):
        attr = super().rss_attributes()
        attr['xmlns:itunes'] = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        return attr

    def add_root_elements(self, handler):
        super().add_root_elements(handler)
        if self.feed['image']:
            handler.startElement('image', {})
            handler.addQuickElement('url', self.feed['image'].url)
            handler.addQuickElement('title', f"{self.feed['title']}'s Picture")
            handler.endElement('image')
            handler.startElement('itunes:image', {'href': self.feed['image'].url})
            handler.endElement('itunes:image')

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        handler.addQuickElement('itunes:duration', str(item['duration']))
        if item['image']:
            handler.startElement('itunes:image', {'href': item['image'].url})
            handler.endElement('itunes:image')


class PodcastFeed(Feed):
    feed_type = iTunesFeed
    host = None

    # overwrite __call__ to add cache control header
    def __call__(self, request, *args, **kwargs):
        response = super().__call__(request, *args, **kwargs)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
        return response

    def get_object(self, request: HttpRequest, **kwargs):
        self.host = request.get_host()
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
        return {'image': podcast.image}

    def items(self, podcast: Podcast):
        return podcast.episode_set.filter(downloaded=True)

    def item_title(self, episode: Episode):
        return episode.name

    def item_link(self, episode: Episode):
        return reverse('podcasts:episode-download', kwargs={'slug': episode.podcast.slug, 'episode_id': episode.id})

    def item_enclosure_url(self, episode: Episode):
        return f'{self.host}{episode.mp3.url}'

    def item_enclosure_length(self, episode: Episode):
        return episode.mp3.size

    def item_enclosure_mime_type(self, item):
        return "audio/mpeg"

    def item_pubdate(self, episode: Episode):
        return episode.pub_date

    def item_description(self, episode: Episode):
        return episode.description

    def item_extra_kwargs(self, episode: Episode):
        return {
            'duration': episode.duration,
            'image': episode.image,
        }
