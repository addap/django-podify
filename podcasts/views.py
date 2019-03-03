# -*- coding: future_fstrings -*-
from django.core.files import File
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse

import os
from django.utils.text import slugify

from .forms import AddPodcastForm
from .models import Podcast, Episode


# Create your views here.
def index(request):
    template_name = 'podcasts/index.html'
    podcast_list = Podcast.objects.all().order_by('pub_date')
    return render(request,
                  template_name,
                  context={'podcast_list': podcast_list})


def add_podcast(request):
    template_name = 'podcasts/add-podcast.html'
    if request.method == "POST":
        form = AddPodcastForm(request.POST)

        if form.is_valid():
            podcast = form.save()

            if form.cleaned_data['mp3_source']:
                mp3s = os.listdir(form.cleaned_data['mp3_source'])
                for mp3 in mp3s:
                    name = os.path.splitext(mp3)[0]
                    slug = slugify(name)
                    episode = podcast.episode_set.create(name=name,
                                                         slug=slug,
                                                         downloaded=True,)
                    with File(open(os.path.join(form.cleaned_data['mp3_source'], mp3), "rb")) as f:
                        episode.mp3.save(f"{slug}.mp3", f)

            # todo remove old files?

            index_url = reverse('podcasts:index')
            return HttpResponseRedirect(index_url)
    else:
        form = AddPodcastForm()

    return render(request, template_name, {'form': form})


def podcast_detail(request, slug):
    template_name = 'podcasts/detail.html'
    podcast = get_object_or_404(Podcast, slug=slug)
    return render(request,
                  template_name,
                  context={'podcast': podcast})


def episode_download(request, slug, episode_id):
    episode = get_object_or_404(Episode, pk=episode_id)

    # if not episode.downloaded:
    #     try:
    #         episode.download()
    #     except Exception:
    #         s = traceback.format_exc()
    #         raise Http404(f"Could not download video to server {s}")

    if episode.downloaded:
        return FileResponse(episode.mp3, as_attachment=True,
                            content_type='audio/mpeg3')
    else:
        raise Http404("Episode not downloaded yet!")


# def podcast_rss(request, slug):
#     """Returns the generated rss feed for the podcast with slug slug. """
#     feedgen = PodcastFeed()
#     feed = feedgen(request, slug)
#     feed['Cache-Control'] = 'no-cache, no-store, must-revalidate, private, max-age=0'
#     return feed
