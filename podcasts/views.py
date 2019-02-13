import os

from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, HttpResponse, Http404
from django.core.files import File
from podify.settings import MEDIA_ROOT
from .models import Podcast, Episode
from .rssgen import generate_from_podcast
import youtube_dl
import traceback


# Create your views here.
def index(request):
    template_name = 'podcasts/index.html'
    podcast_list = Podcast.objects.all().order_by('slug')
    return render(request,
                  template_name,
                  context={'podcast_list': podcast_list})


def podcast_detail(request, slug):
    template_name = 'podcasts/detail.html'
    podcast = get_object_or_404(Podcast, slug=slug)
    return render(request,
                  template_name,
                  context={'podcast': podcast})


def podcast_rss(request, slug):
    podcast = get_object_or_404(Podcast, slug=slug)
    rss_text = generate_from_podcast(podcast)
    # response = FileResponse(rss_text)
    response = FileResponse(rss_text, as_attachment=True,
                            filename=f"{podcast.name}.rss", content_type='application/rss+xml; charset=UTF-8')
    return response


def episode_detail(request, slug, episode_id):
    episode = get_object_or_404(Episode, pk=episode_id)

    if not episode.downloaded:
        filename = f'{MEDIA_ROOT}{episode.name}.mp3'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': filename,
            'quiet': True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
        }
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([episode.url])
            episode.downloaded = True
            with File(open(filename, "rb")) as f:
                episode.mp3.save(f"{episode.name}.mp3", f)
            os.remove(filename)
            episode.save()
        except Exception as e:
            s = traceback.format_exc()
            raise Http404(f"Could not download video to server {s}")

    return FileResponse(episode.mp3, as_attachment=True,
                        content_type='audio/mpeg3')

