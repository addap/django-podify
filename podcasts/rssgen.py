import html
from lxml import etree
from podcasts.models import Podcast, Episode
from django.urls import reverse

# Itunes namespace which needs to be prepended to itunes attributes
ITUNES_NS = "http://www.itunes.com/DTDs/Podcast-1.0.dtd"
# triple { & } because we need two to display a single and a third for the formatting
ITUNES = "{{{0}}}".format(ITUNES_NS)


def generate_from_podcast(podcast: Podcast):
    """Generate an rss file based on the podcast. The urls of the episodes are special urls that initialize the
    download of the episode the first time they are GET'd so that we can actually download it the second time.
    At the moment it only uses one itunes tag for the duration. Have
    to look if there are more that are useful and should be supported
    """
    rss = etree.Element("rss", nsmap={"itunes": ITUNES_NS}, version="2.0")
    channel = create_channel(rss, podcast)

    for episode in podcast.episode_set.all():
        create_episode(episode, podcast, channel)

    return etree\
        .tostring(rss, pretty_print=True, encoding="utf-8", xml_declaration=True)\
        .decode('utf-8')


def create_channel(rss, podcast: Podcast):
    link = reverse('podcasts:podcast-rss', args=(podcast.slug,))

    channel = etree.SubElement(rss, "channel")
    name = html.escape(podcast.name)

    etree.SubElement(channel, "title").text = name
    etree.SubElement(channel, "link").text = link
    etree.SubElement(channel, "description").text = html.escape(podcast.description)

    if podcast.image:
        image = etree.SubElement(channel, "image")
        etree.SubElement(image, "url").text = podcast.image.url
        etree.SubElement(image, "title").text = "{0}'s Picture".format(name)

    return channel


def create_episode(episode: Episode, podcast: Podcast, channel):
    url = reverse('podcasts:episode-detail', kwargs={'slug': podcast.slug, 'episode_id': episode.id})
    # length = str(os.path.getsize(episode.mp3))
    title = html.escape(episode.name)

    item = etree.SubElement(channel, "item")
    etree.SubElement(item, "title").text = title
    etree.SubElement(item, "enclosure", url=url, type="audio/mpeg")#, length=length)
    etree.SubElement(item, "guid").text = url
    etree.SubElement(item, "pubDate").text = episode.pub_date.isoformat()
    etree.SubElement(item, ITUNES + "duration").text = str(episode.duration)
