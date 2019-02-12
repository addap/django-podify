from django.contrib import admin
from podcasts.models import Podcast, Episode
from django.urls import reverse
from django.utils.html import format_html


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
    readonly_fields = ('podcast_actions',)

    inlines = [EpisodeInline]
    list_display = ('name', 'podcast_type', 'podcast_actions')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            self.prepopulated_fields = {}
            return self.readonly_fields + ('slug',)
        return self.readonly_fields

    def podcast_actions(self, obj):
        return format_html('<a class="button" href={}>Sync</a>', reverse("podcasts:podcast-detail", args=[obj.slug]))


admin.site.register(Podcast, PodcastAdmin)
