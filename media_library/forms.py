# -*- coding: utf-8 -*-
from django import forms
from django.utils.translation import ugettext_lazy as _
# from cffmpeg.models import ConvertVideo
#
#
# class ReviewForm(forms.ModelForm):
#     other = forms.CharField(
#         label=_('Other'),
#         required=False,
#         widget=forms.Textarea(attrs={
#             'class': 'form-control',
#             'rows': 3,
#             'style': 'resize: vertical;'
#         }),
#         error_messages={
#             'required': _('Reject reason description'),
#         }
#     )
#
#     def __init__(self, *args, **kwargs):
#         super(ReviewForm, self).__init__(*args, **kwargs)
#
#     class Meta:
#         model = ConvertVideo
#         fields = ('revision', 'reason', 'other',)
