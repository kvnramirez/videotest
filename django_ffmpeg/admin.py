# -*- coding: utf-8 -*-

from django.forms import ModelForm
from django.contrib.admin.widgets import AdminFileWidget
from django.db import models
from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

# from .models import ConvertingCommand, ConvertVideo
from .models import ConvertVideo


class AdminVideoWidget(AdminFileWidget):
    pass
    # def render(self, name, value, attrs=None):
    #     html = super(AdminVideoWidget, self).render(name, value, attrs)
    #     if u'<a href' in html:
    #         parts = html.split('<br />')
    #         html = u'<p class="file-upload">'
    #         if value.instance.convert_status == 'converted' and value.instance.convert_status_mov == 'converted':
    #             html += _('Video %(path)s converted to MOV and MP4<br />') % {'path': value}
    #         elif value.instance.convert_status == 'converted' and not value.instance.convert_status_mov == 'converted':
    #             # html += _('Video %(path)s not converted yet<br />') % {'path':value}
    #             html += _('Video %(path)s converted to MP4 but no MOV<br />') % {'path': value}
    #         elif not value.instance.convert_status == 'converted' and value.instance.convert_status_mov == 'converted':
    #             # html += _('Video %(path)s not converted yet<br />') % {'path':value}
    #             html += _('Video %(path)s converted to MOV but no MP4<br />') % {'path': value}
    #         else:
    #             html += _('Video %(path)s not converted yet<br />') % {'path': value}
    #
    #         html = mark_safe(html + parts[1])
    #     return html


class VideoAdminForm(ModelForm):
    class Meta:
        model = ConvertVideo
        fields = '__all__'
        widgets = {
            'video': AdminVideoWidget,
        }


def reconvert_video(modeladmin, request, queryset):
    queryset.update(convert_status='pending')


reconvert_video.short_description = _('Convert again')


class VideoAdmin(admin.ModelAdmin):
    # list_display = ('title_repr', 'created_at', 'convert_status', 'converted_at')
    list_display = ('title_repr', 'created_at')
    list_display_links = ('title_repr',)
    # readonly_fields = (
    #     'convert_extension', 'convert_status', 'last_convert_msg', 'convert_extension_2', 'convert_status_mov',
    #     'last_convert_msg_mov')
    # readonly_fields = ('enqueue',)
    form = VideoAdminForm

    # actions = [reconvert_video]

    def title_repr(self, obj):
        return str(obj)

    title_repr.short_description = _('Title')

    def save_model(self, request, obj, form, change):
        if 'video' in form.changed_data and change:
            obj.convert_status = 'pending'
        if not change:
            obj.user = request.user
        super(VideoAdmin, self).save_model(request, obj, form, change)


admin.site.register(ConvertVideo, VideoAdmin)

# class ConvertingCommandAdmin(admin.ModelAdmin): pass
#
#
# admin.site.register(ConvertingCommand, ConvertingCommandAdmin)
