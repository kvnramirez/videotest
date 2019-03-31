from django import forms

from django_ffmpeg.models import ConvertVideo


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ConvertVideo
        fields = ('revision', 'reason', 'other',)
