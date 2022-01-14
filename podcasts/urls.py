from django.urls import path

from . import views
from .feeds import PodcastFeed

app_name = 'podcasts'
urlpatterns = [
    path('', views.index, name='index'),
    path('sync', views.podcast_sync_all, name='podcast-sync-all'),
    path('podcast/<slug:slug>/', views.podcast_detail, name='podcast-detail'),
    path('podcast/<slug:slug>/sync', views.podcast_sync, name='podcast-sync'),
    path('podcast/<slug:slug>/rss.xml', PodcastFeed(), name='podcast-rss'),
    path('podcast/<slug:slug>/dummy-episode-sync', views.dummy_episode_sync, name='dummy-episode-sync'),
    path('podcast/<slug:slug>/ep/<slug:episode_slug>', views.episode_download, name='episode-download'),
]
