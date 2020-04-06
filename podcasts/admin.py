from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models.signals import pre_save
from django_q.tasks import async_task
from django_q.tasks import Chain

from .models import Podcast, Episode
from .tasks import podcast_download, podcast_update
from .forms import PodcastModelForm

class EpisodeInline(admin.TabularInline):
    model = Episode
    fields = ['name', 'url', 'downloaded', 'pub_date', 'duration', 'invalid', ]
    readonly_fields = ('downloaded', 'pub_date', 'duration',)
    extra = 0


class PodcastAdmin(admin.ModelAdmin):
    form = PodcastModelForm
    fieldsets = [
        (None, {'fields': [('name', 'slug',),]}),
        ('Metadata', {'fields': ['playlist_url', 'description', 'image', 'pub_date', ]}),
        ('Audio Upload', {'fields': ['audio_upload',]}),
    ]
    readonly_fields = ('pub_date', )
    actions = ['update_podcasts', 'download_podcasts', 'sync_podcasts',]
    prepopulated_fields = {'slug': ('name',)}

    inlines = [EpisodeInline]
    list_display = ('name', 'rss_link')

    def save_model(self, request, obj, form, change):
        # save once so that we can create related episodes
        obj.save()
        form = PodcastModelForm(request.POST, request.FILES)
        if form.is_valid():
            for file in form.cleaned_data['audio_upload']:
                obj.add_episode_mp3(file)

        super().save_model(request, obj, form, change)

    def rss_link(self, model):
        return format_html('<a href="{}">RSS</a>', reverse('podcasts:podcast-rss', args=(model.slug,)))

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

    def sync_podcasts(self, request, queryset):
        for podcast in queryset:
            chain = Chain()
            chain.append(podcast_update, podcast.pk)
            chain.append(podcast_download, podcast.pk)
            chain.run()
            self.message_user(request, "Syncing podcast")

    sync_podcasts.short_description = "Update & download selected podcasts"

admin.site.register(Podcast, PodcastAdmin)
