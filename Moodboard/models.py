from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from PIL import Image
from django.core.files.storage import default_storage as storage
import io


class Tag(models.Model):
    tags = models.CharField(max_length=128)

    def __str__(self):
        return f"{self.tags}"


class TheMoodboard(models.Model):
    projectName = models.CharField(max_length=128)
    picsContained = models.ManyToManyField('Img', blank=True)
    isPrivate = models.BooleanField(default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now=True)
    share_url = models.CharField(max_length=512, unique=True, blank=True, null=True)
    #nsfw = models.BooleanField(default=False, blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f"{self.projectName}"


class Img(models.Model):
    image = models.ImageField(upload_to='static/moodboard/images', blank=True, null=True, help_text="Upload from your device")
    url_img = models.CharField(max_length=256, default='', blank=True, help_text="Or insert a link to image")
    moodboard = models.ForeignKey(TheMoodboard, blank=True, null=True, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"{self.image}"[24:] + f"{self.url_img}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if storage.exists(self.image.name):
            img_read = storage.open(self.image.name, 'rb')
            img = Image.open(img_read)
            if img.format in ['png', 'PNG']:
                try:
                    img = img.convert('RGB')
                    img.save()
                except TypeError:
                    pass
            else:
                width, height = img.size
                resizeby_width = width / 1200
                resizeby_height = height / 1200
                if width > 1200 and height > 1200:
                    aspect_r = width/height
                    if height > width:
                        img = img.resize((int(1200//(1/aspect_r)), 1200), Image.ANTIALIAS)
                    else:
                        img = img.resize((1200, int(1200 // aspect_r)), Image.ANTIALIAS)
                elif width > 1200 or height > 1200:
                    if width > 1200:
                        if height == 0:
                            raise AssertionError(ZeroDivisionError)
                        img = img.resize((1200, int(height//resizeby_width)), Image.ANTIALIAS)
                    else:
                        if width == 0:
                            raise AssertionError(ZeroDivisionError)
                        img = img.resize((int(width//resizeby_height), 1200), Image.ANTIALIAS)

            in_mem_file = io.BytesIO()
            # saving buffer to image file
            img.save(in_mem_file, format='JPEG', quality=95, progressive=True)
            # open file in s3 storage
            img_write = storage.open(self.image.name, 'w+')
            # write buffer as bytes
            img_write.write(in_mem_file.getvalue())
            img_write.close()
            img_read.close()
        else:
            pass
