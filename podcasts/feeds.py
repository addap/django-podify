from django.contrib.syndication.views import Feed
from django.urls import reverse
from django.utils.feedgenerator import Rss201rev2Feed

from .models import Podcast, Episode
from podify.settings import SERVER_URL, MEDIA_ROOT


class iTunesFeed(Rss201rev2Feed):
    def rss_attributes(self):
        attr = super().rss_attributes()
        attr['xmlns:itunes'] = 'http://www.itunes.com/dtds/podcast-1.0.dtd'
        return attr

    def add_root_elements(self, handler):
        super().add_root_elements(handler)
        if self.feed['image']:
            handler.addQuickElement('itunes:image', self.feed['image'].url)

    def add_item_elements(self, handler, item):
        super().add_item_elements(handler, item)
        handler.addQuickElement('itunes:duration', str(item['duration']))
        # if item['image']:
        #     handler.addQuickElement('itunes:image', item['image'].url)


class PodcastFeed(Feed):
    feed_type = iTunesFeed

    def get_object(self, request, slug):
        return Podcast.objects.get(slug=slug)

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

    def item_link(self, episode: Episode):
        return reverse('podcasts:episode-download', kwargs={'slug': episode.podcast.slug, 'episode_id': episode.id})

    def item_enclosure_url(self, episode: Episode):
        return f'{SERVER_URL}{episode.mp3.url}'

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
            # 'image': episode.image,
        }
