import os
from django import forms

from .models import Podcast
from podify.settings import BASE_DIR


class AddPodcastForm(forms.ModelForm):
    mp3_source = forms.FilePathField(allow_files=False,
                                     allow_folders=True,
                                     required=False,
                                     path=os.path.join(BASE_DIR, "local-mp3s"))

    class Meta:
        model = Podcast
        fields = ['name', 'playlist_url', ]

# class AddPodcastForm(forms.Form):
#     name = forms.CharField()
#     playlist_url = forms.URLField(required=False)
#     file_path = forms.FilePathField(path='', required=False)

