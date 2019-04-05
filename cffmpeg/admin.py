# -*- coding: utf-8 -*-
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.forms import ModelForm
from django.contrib.admin.widgets import AdminFileWidget
from django.db import models
from django.contrib import admin
from django.forms import CheckboxSelectMultiple
from django.urls import reverse
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

# from .models import ConvertingCommand, ConvertVideo
from .models import ConvertVideo, EnqueuedVideo


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


class EnqueueVideoInline(admin.TabularInline):
    can_delete = False
    extra = 0
    model = ConvertVideo.enqueue.through
    verbose_name = _('Enqueued video')
    verbose_name_plural = _('Enqueued videos')
    template = 'tabular.html'
    show_change_link = True

    # def __init__(self, parent_model, admin_site):
    #     self.admin_site = admin_site
    #     self.parent_model = parent_model
    #     self.opts = self.model._meta
    #     self.has_registered_model = True
    #     overrides = FORMFIELD_FOR_DBFIELD_DEFAULTS.copy()
    #     overrides.update(self.formfield_overrides)
    #     self.formfield_overrides = overrides
    #     if self.verbose_name is None:
    #         self.verbose_name = self.model._meta.verbose_name
    #     if self.verbose_name_plural is None:
    #         self.verbose_name_plural = self.model._meta.verbose_name_plural

    def has_add_permission(self, request):
        return False

    # def has_change_permission(self, request, obj=None):
    #     return False

    # def has_delete_permission(self, request, obj=None):
    #     return False

    fields = ['enqueue_pk', 'enqueue_lcm', 'enqueue_status', 'enqueue_ext', 'enqueue_target', 'enqueue_cdate',
              'enqueue_link']
    readonly_fields = ['enqueue_pk', 'enqueue_lcm', 'enqueue_status', 'enqueue_ext', 'enqueue_target',
                       'enqueue_cdate', 'enqueue_link']

    def enqueue_link(self, instance):
        print 'admin:%s_%s_change' % (instance.enqueuedvideo._meta.app_label,
                                      instance.enqueuedvideo._meta.model_name)
        url = reverse('admin:%s_%s_change' % (instance.enqueuedvideo._meta.app_label,
                                              instance.enqueuedvideo._meta.model_name),
                      args=(instance.id,))

        return format_html(u'<a class="button" href="{}">{}</a>', url, _('View Details'))
        # … or if you want to include other fields:
        # return format_html(u'<a href="{}">Edit: {}</a>', url, instance.title)

    enqueue_link.short_description = _('Actions')

    def enqueue_pk(self, instance):
        # print instance.__dict__
        # print instance.enqueuedvideo.__dict__
        return instance.enqueuedvideo.pk

    enqueue_pk.short_description = _('Pk')

    def enqueue_lcm(self, instance):
        return instance.enqueuedvideo.last_convert_msg

    enqueue_lcm.short_description = _('Last message')

    def enqueue_status(self, instance):
        convert_status = instance.enqueuedvideo.convert_status
        print convert_status
        if convert_status == 'error':
            output = format_html(u'<b style="color: #FF0000;">{}</b>',
                                 instance.enqueuedvideo.get_convert_status_display())
        elif convert_status == 'converted':
            output = format_html(u'<b style="color: #7FFF00;">{}</b>',
                                 instance.enqueuedvideo.get_convert_status_display())
        else:
            output = instance.enqueuedvideo.get_convert_status_display()
        return output

    enqueue_status.short_description = _('Status')

    def enqueue_ext(self, instance):
        return instance.enqueuedvideo.convert_extension

    enqueue_ext.short_description = _('Extension')

    def enqueue_cdate(self, instance):
        x = instance.enqueuedvideo.converted_at
        y = x.strftime('%Y-%m-%d %H:%M')
        return y

    enqueue_cdate.short_description = _('Convertion date')

    def enqueue_target(self, instance):
        if instance.enqueuedvideo.convert_extension:
            if instance.enqueuedvideo.convert_extension == 'mov':
                return _('Apple devices')
            else:
                return _('Other devices')
        return '-'

    enqueue_target.short_description = _('Device Target')


class VideoAdmin(admin.ModelAdmin):
    # list_display = ('title_repr', 'created_at', 'convert_status', 'converted_at')
    list_display = ('title_repr', 'created_at',)
    list_display_links = ('title_repr',)
    # readonly_fields = (
    #     'convert_extension', 'convert_status', 'last_convert_msg', 'convert_extension_2', 'convert_status_mov',
    #     'last_convert_msg_mov')
    # readonly_fields = ('enqueue',)
    form = VideoAdminForm

    inlines = [
        EnqueueVideoInline,
    ]
    exclude = ('enqueue',)

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


class EnqueuedVideoAdmin(admin.ModelAdmin):
    readonly_fields = (
        'converted_video', 'thumb', 'thumb_frame', 'convert_status', 'converted_at', 'last_convert_msg',
        'full_convert_msg', 'meta_info', 'convert_extension', 'command', 'thumb_command')


admin.site.register(EnqueuedVideo, EnqueuedVideoAdmin)

admin.site.register(ConvertVideo, VideoAdmin)
