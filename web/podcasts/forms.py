from django import forms
from .models import Podcast

# from https://docs.djangoproject.com/en/4.1/topics/http/file-uploads/#uploading-multiple-files
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result


class FileFieldForm(forms.Form):
    file_field = MultipleFileField()

class PodcastModelForm(forms.ModelForm):
    '''Form derived from the Podcast model with a multi-file audio upload input.'''
    audio_upload = MultipleFileField()
    audio_upload.required = False

    class Meta:
        model = Podcast
        fields = []