from django.urls import path

from . import views

app_name = 'podcasts'

urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:slug>/', views.detail, name='detail'),
    path('<slug:slug>/rss', views.rss, name='rss'),
]
