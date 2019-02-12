from django.contrib import admin
from podcasts.models import Podcast, Episode


# Register your models here.
class EpisodeInline(admin.TabularInline):
    model = Episode
    fields = ['name', 'url', 'mp3', 'downloaded', ]
    extra = 0


class PodcastAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'podcast_type', 'slug', ]}),
        ('Metadata', {'fields': ['url', 'description', 'image', ]})
    ]
    prepopulated_fields = {'slug': ('name',)}

    inlines = [EpisodeInline]
    list_display = ('name', 'podcast_type')


admin.site.register(Podcast, PodcastAdmin)
