import io
from django.shortcuts import render, get_object_or_404
from django.http import FileResponse, HttpResponse
from .models import Podcast, Episode
from .rssgen import generate_from_podcast

# Create your views here.
def index(request):
    template_name = 'podcasts/index.html'
    podcast_list = Podcast.objects.all().order_by('title')
    return render(request,
                  template_name,
                  context={'podcast_list': podcast_list})

def detail(request, podcast_title):
    template_name = 'podcasts/detail.html'
    podcast = get_object_or_404(Podcast, title=podcast_title)
    return render(request,
                  template_name,
                  context={'podcast' : podcast})

def rss(request, podcast_title):
    podcast = get_object_or_404(Podcast, title=podcast_title)
    rss = generate_from_podcast(podcast)
    response = FileResponse(rss, as_attachment=True, filename=f"{podcast.title}.rss", content_type='application/rss+xml; charset=UTF-8')
    return response
    
