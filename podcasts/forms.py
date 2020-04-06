from django import forms
from multiupload.fields import MultiMediaField

from .models import Podcast

class PodcastModelForm(forms.ModelForm):
    # https://github.com/Chive/django-multiupload/
    audio_upload = MultiMediaField(min_num=1, media_type='audio')
    audio_upload.required = False

    class Meta:
        model = Podcast
        fields = []