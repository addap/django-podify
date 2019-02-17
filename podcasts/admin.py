from django.contrib import admin
from django.urls import path, reverse

from podcasts.models import Podcast, Episode


# Register your models here.
class EpisodeInline(admin.TabularInline):
    model = Episode
    fields = ['name', 'url', 'downloaded', 'pub_date', 'duration', ]
    readonly_fields = ('downloaded', 'pub_date', 'duration', )
    extra = 0


class PodcastAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'podcast_type', 'slug', ]}),
        ('Metadata', {'fields': ['url', 'description', 'image', 'pub_date', ]})
    ]
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('pub_date', )
    actions = ['update_podcasts', 'download_podcasts', ]

    inlines = [EpisodeInline]
    list_display = ('name', 'podcast_type', )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.prepopulated_fields = {}
            return self.readonly_fields + ('slug',)
        return self.readonly_fields

    # def get_urls(self):
    #     urls = super().get_urls()
    #     my_urls = [
    #         path('download/', self.download_podcasts),
    #         path('update/', self.update_podcasts),
    #     ]
    #     return my_urls + urls

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
