from django.contrib import admin
from podcasts.models import Podcast, Episode


# Register your models here.
class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 0


class PodcastAdmin(admin.ModelAdmin):
    fields = ['name', 'podcast_type', 'url']

    inlines = [EpisodeInline]
    list_display = ('name', 'podcast_type')


admin.site.register(Podcast, PodcastAdmin)
