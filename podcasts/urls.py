from django.urls import path

from podcasts.feeds import PodcastFeed
from . import views

app_name = 'podcasts'

urlpatterns = [
    path('', views.index, name='index'),
    path('add-podcast/', views.add_podcast, name='add-podcast'),
    path('<slug:slug>/', views.podcast_detail, name='podcast-detail'),
    path('<slug:slug>/rss', PodcastFeed(), name='podcast-rss'),
    path('<slug:slug>/ep/<int:episode_id>', views.episode_download, name='episode-download'),
]
