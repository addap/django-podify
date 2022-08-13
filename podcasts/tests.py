from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify
from django_q.tasks import result_group

from .models import Podcast

playlist_urls = [
    ('Podcast normal test',
     'https://www.youtube.com/playlist?list=PL-PEOyl2c0APYdsJJz56YZSRmYgJV6K4O'),
    ('Podcast unavailable test',
     'https://www.youtube.com/playlist?list=PL-PEOyl2c0AOYazAq7ohtyu3wF6FOvC4K'),
]

normal_podcast_rss = b'<?xml version="1.0" encoding="utf-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"><channel><title>Normal Podcast</title><link>http://testserver/normal-podcast/</link><description>Podify normal test description</description><atom:link href="http://testserver/normal-podcast/rss" rel="self"></atom:link><language>en-us</language><lastBuildDate>Sat, 28 May 2011 06:51:33 +0000</lastBuildDate><image><url>/media/thumbnails/normal-podcast.jpg</url><title>Normal Podcast\'s Picture</title></image><itunes:image href="/media/thumbnails/normal-podcast.jpg"></itunes:image><item><title>Getting to Know Her</title><link>http://testserver/normal-podcast/ep/1</link><description>There is a battle that rages in all men, between the cordial fellow attempting conversation and the wounded, jealous cad expecting athletic sex in the near-future. Woe unto the red and white Battleship (TM) pieces that are caught in such a crossfire of the soul.\n\nVine: https://vine.co/5sf\nFacebook: https://www.facebook.com/5secondfilms\nTwitter: https://twitter.com/5sf\nInstagram: https://instagram.com/5sf\nSubscribe: https://www.youtube.com/5secondfilms</description><pubDate>Sat, 28 May 2011 06:51:33 +0000</pubDate><guid>http://testserver/normal-podcast/ep/1</guid><enclosure length="128672" type="audio/mpeg" url="testserver/media/mp3s/getting-to-know-her.mp3"></enclosure><itunes:duration>0:00:08</itunes:duration><itunes:image href="/media/thumbnails/getting-to-know-her.jpg"></itunes:image></item></channel></rss>'
unavailable_podcast_rss = b'<?xml version="1.0" encoding="utf-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"><channel><title>Podcast unavailable test</title><link>http://testserver/podcast-unavailable-test/</link><description>Podify unavailable test description</description><atom:link href="http://testserver/podcast-unavailable-test/rss" rel="self"></atom:link><language>en-us</language><lastBuildDate>Tue, 20 Jan 2015 14:03:51 +0000</lastBuildDate><image><url>/media/thumbnails/podcast-unavailable-test.jpg</url><title>Podcast unavailable test\'s Picture</title></image><itunes:image href="/media/thumbnails/podcast-unavailable-test.jpg"></itunes:image><item><title>Bad Sandwich</title><link>http://testserver/podcast-unavailable-test/ep/2</link><description>Sometimes I have dreams that I\'m back in high school, about to get onstage in "Inherit the Wind," and I\'ve forgotten all my lines as Henry Drummond. I approach the edge of the stage and my father cries, knowing his son is a failure, when I open my mouth and a fully-formed sandwich comes gurgling out.\n\nIt falls into my hands. It\'s a turkey sandwich with 1 slice of ham for good measure, and ripe cherry tomatoes sliced in half. The lettuce is still wet from being washed, as crisp as the toasted ciabatta bun. The audience is nonplussed, arms folded. They know I don\'t know my lines. This is not what they paid for.\n\nA cough from the back, signifying nothing. Sometimes it\'s my mother coughing, other times it\'s a full-grown bear.\n\nI bring the sandwich to my mouth and begin to take a bite, completely at a loss of what else to do. The crowd erupts in groans of "Oh come ON" and "Of course he\'d eat the fucking sandwich" and "GET OFF THE STAGE." Boos threaten to usurp the student union. And I\'m just crying there, mulling the turkey and ciabatta in my mouth. It tastes pretty good.\n\nVine: https://vine.co/5sf\nSubscribe: https://www.youtube.com/5secondfilms\nFacebook: https://www.facebook.com/5secondfilms\nTwitter: https://twitter.com/5sf\nInstagram: https://instagram.com/5sf</description><pubDate>Tue, 20 Jan 2015 14:03:51 +0000</pubDate><guid>http://testserver/podcast-unavailable-test/ep/2</guid><enclosure length="129040" type="audio/mpeg" url="testserver/media/mp3s/bad-sandwich.mp3"></enclosure><itunes:duration>0:00:08</itunes:duration><itunes:image href="/media/thumbnails/bad-sandwich.jpg"></itunes:image></item></channel></rss>'


def create_podcast(name, url="") -> Podcast:
    podcast = Podcast(name=name, slug=slugify(name), playlist_url=url)
    podcast.save()
    return podcast


class PodcastModelTests(TestCase):
    playlist_url: str = "https://www.youtube.com/playlist?list=PL-PEOyl2c0AN3e2ZRSXcLrye7k_M0C9cW"
    p1: Podcast = None

    def tearDown(self):
        if self.p1:
            self.p1.delete()

    # def test_create(self):
    #     self.p1 = create_podcast("Normal Podcast", self.playlist_url)
    #     response = self.client.get(reverse('podcasts:index'))
    #     self.assertContains(response, self.p1.name)

    def test_update(self):
        self.p1 = create_podcast("Normal Podcast", self.playlist_url)
        self.p1.update()
        result_group(self.p1.slug, wait=-1)

    # def test_no_playlist(self):
    #     response = self.client.get(reverse('podcasts:index'))
    #     self.assertContains(response, "No podcasts available")

    # def test_podcast_detail(self):
    #     self.p1 = create_podcast("Normal Podcast",
    #                              'https://www.youtube.com/playlist?list=PL-PEOyl2c0APYdsJJz56YZSRmYgJV6K4O')
    #     response = self.client.get(
    #         reverse('podcasts:podcast-detail', args=(self.p1.slug,)))
    #     self.assertEqual(response.status_code, 200)

    # def test_normal_playlist_rss(self):
    #     self.p1 = create_podcast("Normal Podcast",
    #                              'https://www.youtube.com/playlist?list=PL-PEOyl2c0APYdsJJz56YZSRmYgJV6K4O')
    #     self.p1.download()
    #     response = self.client.get(
    #         reverse('podcasts:podcast-rss', args=(self.p1.slug,)))
    #     self.assertEqual(response.content, normal_podcast_rss)

    # def test_unavailable_playlist_rss(self):
    #     self.p1 = create_podcast("Podcast unavailable test",
    #                              'https://www.youtube.com/playlist?list=PL-PEOyl2c0AOYazAq7ohtyu3wF6FOvC4K')
    #     self.p1.download()
    #     response = self.client.get(
    #         reverse('podcasts:podcast-rss', args=(self.p1.slug,)))
    #     # print(response.content)
    #     self.assertEqual(response.content, unavailable_podcast_rss)
