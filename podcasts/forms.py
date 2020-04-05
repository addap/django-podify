from django import forms
from multiupload.fields import MultiMediaField

from .models import Podcast


class AddPodcastForm(forms.ModelForm):
    class Meta:
        model = Podcast
        fields = ['name', 'playlist_url', ]


class UploadMP3Form(forms.Form):
    # https://github.com/Chive/django-multiupload/
    mp3s = MultiMediaField(
        min_num=1,
        media_type='audio'
    )
