import time
from django.test import TestCase
from django.urls import reverse
from django.utils.text import slugify
from django_q.tasks import result_group

from .models import Podcast


def create_podcast(name, url="") -> Podcast:
    podcast = Podcast.objects.create(
        name=name, slug=slugify(name), playlist_url=url)
    return podcast


class PodcastModelTests(TestCase):
    playlist_url: str = "https://www.youtube.com/playlist?list=PL-PEOyl2c0AN3e2ZRSXcLrye7k_M0C9cW"
    episode_url: str = "https://www.youtube.com/watch?v=K61k1Rj0uhI"
    deleted_episode_url: str = "https://www.youtube.com/watch?v=e67nHTbygXs"
    p1: Podcast = None

    def tearDown(self):
        if self.p1:
            self.p1.delete()

    def test_create(self):
        self.p1 = create_podcast("Normal Podcast", self.playlist_url)
        response = self.client.get(reverse('podcasts:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.p1.name)

    def test_update(self):
        self.p1 = create_podcast("Normal Podcast", self.playlist_url)
        self.p1.update()

        # wait 30s until downloads are finished
        result_group(self.p1.slug, wait=30_000)

        self.assertEqual(self.p1.episode_set.count(), 1)

        for e in self.p1.episode_set.all():
            self.assert_(not e.invalid)
            self.assert_(e.initialized)
            self.assert_(e.downloaded)
            self.assert_(e.mp3.url.startswith(
                f'/media/{self.p1.slug}/{e.slug}'))

    def test_dummy_download(self):
        self.p1 = create_podcast("Normal Podcast", self.playlist_url)

        dummy_url = reverse('podcasts:dummy-episode-sync',
                            kwargs={'slug': self.p1.slug})
        print(f"Dummy url {dummy_url}")
        response = self.client.get(dummy_url)

        self.assertEqual(418, response.status_code)

        # wait 30s until downloads are finished
        result_group(self.p1.slug, wait=30_000)

        self.assertEqual(self.p1.episode_set.count(), 1)

        for e in self.p1.episode_set.all():
            self.assert_(not e.invalid)
            self.assert_(e.initialized)
            self.assert_(e.downloaded)
            self.assert_(e.mp3.url.startswith(
                f'/media/{self.p1.slug}/{e.slug}'))

    def test_remove_episode(self):
        self.p1 = create_podcast("Normal Podcast", self.playlist_url)

        self.p1.episode_set.create(url=self.episode_url, from_playlist=False)
        self.assertEqual(self.p1.episode_set.count(), 1)

        # should not delete the episode above
        self.p1.update()

        # wait 30s until downloads are finished
        result_group(self.p1.slug, wait=30_000)

        self.assertEqual(self.p1.episode_set.count(), 2)

        for e in self.p1.episode_set.all():
            self.assert_(not e.invalid)
            self.assert_(e.initialized)
            self.assert_(e.downloaded)
            self.assert_(e.mp3.url.startswith(
                f'/media/{self.p1.slug}/{e.slug}'))

    def test_remove_episode2(self):
        self.p1 = create_podcast("Normal Podcast", self.playlist_url)

        self.p1.episode_set.create(url=self.episode_url, from_playlist=True)
        self.assertEqual(self.p1.episode_set.count(), 1)

        # should not delete the episode above
        self.p1.update()

        # wait 30s until downloads are finished
        result_group(self.p1.slug, wait=30_000)

        self.assertEqual(self.p1.episode_set.count(), 1)

        for e in self.p1.episode_set.all():
            self.assert_(not e.invalid)
            self.assert_(e.initialized)
            self.assert_(e.downloaded)
            self.assert_(e.mp3.url.startswith(
                f'/media/{self.p1.slug}/{e.slug}'))

    def test_no_playlist(self):
        response = self.client.get(reverse('podcasts:index'))
        self.assertContains(response, "No podcasts available")

    def test_podcast_detail(self):
        self.p1 = create_podcast("Normal Podcast", self.playlist_url)

        response = self.client.get(
            reverse('podcasts:podcast-detail', kwargs={'slug': self.p1.slug}))
        self.assertEqual(response.status_code, 200)

    def test_normal_playlist_rss(self):
        self.p1 = create_podcast("Normal Podcast", self.playlist_url)
        self.p1.update()

        # wait 30s until downloads are finished
        result_group(self.p1.slug, wait=30_000)

        response = self.client.get(
            reverse('podcasts:podcast-rss', kwargs={'slug': self.p1.slug}))
        self.assertEqual(response.status_code, 200)

    def test_download_deleted_episode(self):
        self.p1 = create_podcast("Normal Podcast", "")
        self.p1.episode_set.create(url=self.deleted_episode_url)

        self.p1.update()

        # wait 30s until downloads are finished
        result_group(self.p1.slug, wait=30_000)

        for e in self.p1.episode_set.all():
            self.assert_(e.invalid)
            self.assert_(not e.initialized)
            self.assert_(not e.downloaded)

    # def test_unavailable_playlist_rss(self):
    #     self.p1 = create_podcast("Podcast unavailable test",
    #                              'https://www.youtube.com/playlist?list=PL-PEOyl2c0AOYazAq7ohtyu3wF6FOvC4K')
    #     self.p1.download()
    #     response = self.client.get(
    #         reverse('podcasts:podcast-rss', args=(self.p1.slug,)))
    #     # print(response.content)
    #     self.assertEqual(response.content, unavailable_podcast_rss)
