from django.db.models.signals import post_save, pre_save
# from video_encoding.models import Format
from django.dispatch import receiver


# @receiver(post_save, sender=Format)
# def format_post_save(sender, instance, **kwargs):
#     print 'Format post_save'
#     if instance.id is None:  # new object will be created
#         pass  # write your code hier
#     else:
#         print 'Progress:'
#         print instance.progress
#         print '----'
#
#
# @receiver(pre_save, sender=Format)
# def format_pre_save(sender, instance, **kwargs):
#     print 'Format pre_save'
