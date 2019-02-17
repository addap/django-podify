from django.contrib import admin

from podcasts.models import Podcast, Episode


# Register your models here.
class EpisodeInline(admin.TabularInline):
    model = Episode
    fields = ['name', 'url', 'downloaded', 'pub_date', 'duration', 'mp3', ]
    readonly_fields = ('downloaded', 'pub_date', 'duration', 'mp3', )
    extra = 0


class PodcastAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'podcast_type', 'slug', ]}),
        ('Metadata', {'fields': ['url', 'description', 'image', 'pub_date', ]})
    ]
    readonly_fields = ('pub_date', 'slug', )
    actions = ['update_podcasts', 'download_podcasts', ]

    inlines = [EpisodeInline]
    list_display = ('name', 'podcast_type', )

    def update_podcasts(self, request, queryset):
        for podcast in queryset:
            s = podcast.update_podcast()
            self.message_user(request, s)
            podcast.save()

    update_podcasts.short_description = "Update selected podcasts"

    def download_podcasts(self, request, queryset):
        for podcast in queryset:
            s = podcast.download_podcast()
            self.message_user(request, s)
            podcast.save()

    download_podcasts.short_description = "Download selected podcasts"


admin.site.register(Podcast, PodcastAdmin)
