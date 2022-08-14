from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models.signals import pre_save
from django_q.tasks import async_task
from django_q.tasks import Chain

from .models import Podcast, Episode
from .tasks import podcast_update
from .forms import PodcastModelForm


class EpisodeInline(admin.TabularInline):
    model = Episode
    fields = ['name', 'url', 'initialized',
              'pub_date', 'duration', 'invalid', ]
    readonly_fields = ('initialized', 'pub_date', 'duration',)
    extra = 0


class PodcastAdmin(admin.ModelAdmin):
    form = PodcastModelForm
    fieldsets = [
        (None, {'fields': [('name', 'slug',), ]}),
        ('Metadata', {'fields': ['playlist_url',
         'description', 'image', 'pub_date', ]}),
        ('Audio Upload', {'fields': ['audio_upload', ]}),
    ]
    readonly_fields = ('pub_date', )
    actions = ['update_podcasts']
    prepopulated_fields = {'slug': ('name',)}

    inlines = [EpisodeInline]
    list_display = ('name', 'rss_link')

    def save_model(self, request, obj: Podcast, form, change):
        # save once so that we can create related episodes
        obj.save()
        form = PodcastModelForm(request.POST, request.FILES)
        # TODO add reference to django docs
        files = request.FILES.getlist('audio_upload')
        if form.is_valid():
            for file in files:
                obj.add_episode_upload_mp3(file)

        super().save_model(request, obj, form, change)

    def rss_link(self, model):
        return format_html('<a href="{}">RSS</a>', reverse('podcasts:podcast-rss', args=(model.slug,)))

    def update_podcasts(self, request, queryset):
        for podcast in queryset:
            async_task(podcast_update, podcast.pk)
            self.message_user(request, f"Updating podcast {podcast.name}")

    update_podcasts.short_description = "Update selected podcasts"


admin.site.register(Podcast, PodcastAdmin)
