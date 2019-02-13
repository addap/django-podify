from django.contrib import admin
from django.urls import path, reverse

from podcasts.models import Podcast, Episode


# Register your models here.
class EpisodeInline(admin.TabularInline):
    model = Episode
    # fields = ['name', 'url', ]
    exclude = ['mp3']
    readonly_fields = ('downloaded', 'pub_date', 'duration', )
    extra = 0


class PodcastAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'podcast_type', 'slug', ]}),
        ('Metadata', {'fields': ['url', 'description', 'image', ]})
    ]
    prepopulated_fields = {'slug': ('name',)}
    actions = ['sync_podcasts', ]

    inlines = [EpisodeInline]
    list_display = ('name', 'podcast_type', )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.prepopulated_fields = {}
            return self.readonly_fields + ('slug',)
        return self.readonly_fields

    def get_urls(self):
        urls = super().get_urls()
        new_urls = [path('sync/', self.sync_podcasts)]
        return new_urls + urls

    def sync_podcasts(self, request, queryset):
        for podcast in queryset:
            podcast.sync_podcast()
            podcast.save()
            self.message_user(request, f"Synced podcast {podcast}")

    sync_podcasts.short_description = "Sync selected podcasts"


admin.site.register(Podcast, PodcastAdmin)
