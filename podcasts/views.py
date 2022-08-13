from django.http import FileResponse, Http404, HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django_q.tasks import Chain

from .models import Podcast, Episode
from .tasks import podcast_update


def index(request):
    template_name = 'podcasts/index.html'
    podcast_list = Podcast.objects.all().order_by('pub_date')
    return render(request,
                  template_name,
                  context={'podcast_list': podcast_list})


def podcast_detail(request, slug):
    podcast = get_object_or_404(Podcast, slug=slug)
    template_name = 'podcasts/detail.html'

    return render(request,
                  template_name,
                  context={'podcast': podcast, })


def episode_download(request, slug, episode_slug):
    episode = get_object_or_404(Episode, slug=episode_slug, podcast__slug=slug)

    if episode.downloaded:
        return FileResponse(episode.mp3, as_attachment=True,
                            content_type='audio/mpeg')
    else:
        raise Http404("Podify: Episode not downloaded yet.")


def podcast_sync_all(request):
    for podcast in Podcast.objects.all():
        chain = Chain()
        chain.append(podcast_update, podcast.pk)
        # chain.append(podcast_download, podcast.pk)
        chain.run()

    return HttpResponseRedirect(reverse('podcasts:index'))


def podcast_sync(request, slug):
    podcast = get_object_or_404(Podcast, slug=slug)

    chain = Chain()
    chain.append(podcast_update, podcast.pk)
    # chain.append(podcast_download, podcast.pk)
    chain.run()

    return HttpResponseRedirect(reverse('podcasts:podcast-detail', args=(slug,)))


def dummy_episode_sync(request, slug):
    podcast = get_object_or_404(Podcast, slug=slug)

    chain = Chain()
    chain.append(podcast_update, podcast.pk)
    # chain.append(podcast_download, podcast.pk)
    chain.run()

    # return FileResponse(open('media/dummy.m4a', 'rb'), as_attachment=True,
    #                     content_type='audio/mpeg')

    return HttpResponse(f"Sucessfully Updated Podcast {podcast.name}", status=418)
