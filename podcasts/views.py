from django.http import FileResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django_q.tasks import Chain

from .forms import AddPodcastForm, UploadMP3Form
from .models import Podcast, Episode
from .tasks import podcast_download, podcast_update


# Create your views here.
def index(request):
    template_name = 'podcasts/index.html'
    podcast_list = Podcast.objects.all().order_by('pub_date')
    return render(request,
                  template_name,
                  context={'podcast_list': podcast_list})


def add_podcast(request):
    if request.method == "POST":
        form = AddPodcastForm(request.POST)

        if form.is_valid():
            form.save()

            index_url = reverse('podcasts:index')
            return HttpResponseRedirect(index_url)

    form = AddPodcastForm()
    template_name = 'podcasts/add-podcast.html'

    return render(request, template_name, {'form': form})


def podcast_detail(request, slug):
    podcast = get_object_or_404(Podcast, slug=slug)

    if request.method == 'POST':
        form = UploadMP3Form(request.POST, request.FILES)
        if form.is_valid():
            for file in form.cleaned_data['mp3s']:
                podcast.add_episode_mp3(file)

    form = UploadMP3Form()
    template_name = 'podcasts/detail.html'

    return render(request,
                  template_name,
                  context={'podcast': podcast, 'form': form})


def episode_download(request, slug, episode_slug):
    episode = get_object_or_404(Episode, slug=episode_slug, podcast__slug=slug)

    if episode.downloaded:
        return FileResponse(episode.mp3, as_attachment=True,
                            content_type='audio/mpeg3')
    else:
        raise Http404("Podify: Episode not downloaded yet.")


def podcast_sync_all(request):
    for podcast in Podcast.objects.all():
        chain = Chain(cached=True)
        chain.append(podcast_update, podcast.pk)
        chain.append(podcast_download, podcast.pk)
        chain.run()

    return HttpResponseRedirect(reverse('podcasts:index'))


def podcast_sync(request, slug):
    podcast = get_object_or_404(Podcast, slug=slug)

    chain = Chain(cached=True)
    chain.append(podcast_update, podcast.pk)
    chain.append(podcast_download, podcast.pk)
    chain.run()

    return HttpResponseRedirect(reverse('podcasts:podcast-detail', args=(slug,)))

# def podcast_rss(request, slug):
#     """Returns the generated rss feed for the podcast with slug slug. """
#     feedgen = PodcastFeed()
#     feed = feedgen(request, slug)
#     feed['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
#     return feed
