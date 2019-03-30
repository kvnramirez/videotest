from django.db.models.signals import post_save, pre_save

from media_library.models import Video_revision
from video_encoding.models import Format
from django.dispatch import receiver


@receiver(post_save, sender=Format)
def format_post_save(sender, instance, **kwargs):
    print 'Format post_save'
    if instance.id is None:  # new object will be created
        pass  # write your code hier
    else:
        print 'Progress:'
        print instance.progress
        print '----'
        if instance.progress == 100:
            print "video conversion finished, handle here"
            print instance.video
            if instance.video:
                print "instance.video exists, getting review"
                print instance.video.format_set.all()
                print "success videos count: " + str(len(instance.video.format_set.complete().all()))
                print "failed videos count: " + str(len(instance.video.format_set.fail().all()))
                review, created = Video_revision.objects.get_or_create(file=instance.video)
                print "review got"
                print review
                print "updating review"
                review.visible = True
                review.save()

                # TODO si algun video tiene error, entonces fallo y hay que indicar reporte como fallo


@receiver(pre_save, sender=Format)
def format_pre_save(sender, instance, **kwargs):
    print 'Format pre_save'
