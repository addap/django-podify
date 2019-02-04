from django.urls import path

from . import views

app_name = 'podcasts'

urlpatterns = [
    path('', views.index, name='index'),
    path('<podcast_title>/', views.detail, name='detail'),
    path('<podcast_title>/rss', views.rss, name='rss'),
]
