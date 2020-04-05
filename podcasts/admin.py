from django.contrib import admin
from django_q.tasks import async_task

from podcasts.models import Podcast, Episode
from podcasts.tasks import podcast_download, podcast_update


class EpisodeInline(admin.TabularInline):
    model = Episode
    fields = ['name', 'url', 'downloaded', 'pub_date', 'duration', 'invalid', ]
    readonly_fields = ('downloaded', 'pub_date', 'duration',)
    extra = 0


class PodcastAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/admin/inline.css',)
        }

    fieldsets = [
        (None, {'fields': ['name', 'slug', ]}),
        ('Metadata', {'fields': ['playlist_url', 'description', 'image', 'pub_date', ]})
    ]
    readonly_fields = ('pub_date', 'slug',)
    actions = ['update_podcasts', 'download_podcasts', ]

    inlines = [EpisodeInline]
    list_display = ('name',)

    def update_podcasts(self, request, queryset):
        for podcast in queryset:
            async_task(podcast_update, podcast.pk)
            self.message_user(request, "Updating podcast")

    update_podcasts.short_description = "Update selected podcasts"

    def download_podcasts(self, request, queryset):
        for podcast in queryset:
            async_task(podcast_download, podcast.pk)
            self.message_user(request, "Downloading podcast")

    download_podcasts.short_description = "Download selected podcasts"


admin.site.register(Podcast, PodcastAdmin)
