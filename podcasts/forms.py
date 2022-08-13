from django import forms

from .models import Podcast


class PodcastModelForm(forms.ModelForm):
    '''Form derived from the Podcast model with a multi-file audio upload input.'''
    audio_upload = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'multiple': True}))
    audio_upload.required = False

    class Meta:
        model = Podcast
        fields = []
