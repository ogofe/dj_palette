from django.db import models
import uuid

def generate_uuid():
    _id = uuid.uuid4()
    return _id


# Create your models here.
class Page(models.Model):
    title = models.CharField(max_length=200)
    html_content = models.TextField(blank=True, null=True)
    elements = models.ManyToManyField("Element", blank=True)
    element_ordering = models.TextField(blank=True, null=True)
    image = models.ImageField(blank=True, null=True, upload_to='images/')
    url = models.CharField(max_length=200, blank=True, null=True)
    published = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    

class Element(models.Model):
    element_type = None
    element_id = models.UUIDField(default=generate_uuid)
    html_content = models.TextField(blank=True, null=True)
    children = models.ManyToManyField('self', blank=True)

    def __str__(self):
        return f'{self.element_type or "div" }-{self.element_id}'


class YoutubeSnippet(models.Model):
    video_id = models.CharField(max_length=20)
    thumbnail_url = models.URLField(blank=True, null=True)
    channel_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    start_time = models.CharField(max_length=20, blank=True, null=True)
    stop_time = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return self.title

    @property
    def url(self):
        return "https://youtube.com?watch={}{}{}".format(
            self.video_id, 
            f'&start{self.start_time}' if self.start_time else '', 
            f'&start{self.stop_time}' if self.stop_time else '', 
        )
    
