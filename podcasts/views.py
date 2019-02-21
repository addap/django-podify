# -*- coding: future_fstrings -*-
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, HttpResponse, Http404
from .models import Podcast, Episode


# Create your views here.
def index(request):
    template_name = 'podcasts/index.html'
    podcast_list = Podcast.objects.all().order_by('pub_date')
    return render(request,
                  template_name,
                  context={'podcast_list': podcast_list})


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
