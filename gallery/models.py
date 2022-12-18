from django.db import models
from django.utils.text import slugify

# Create your models here.

class GalleryItem(models.Model):
    """Gallery Item"""
    slug = models.SlugField(unique=True, blank=True, null=True)
    make = models.CharField(max_length=45)
    model = models.CharField(max_length=45)
    trim = models.CharField(max_length=45)
    year = models.IntegerField()
    description = models.TextField()
    published = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.id} {self.make} {self.model} {self.trim}'

    class Meta:
        ordering = ['-id']

    def save(self, *args, **kwargs):
        self.slug = slugify(f'{self.make} {self.model} {self.trim} {self.year}')
        super(GalleryItem).save(*args, **kwargs)

class GalleryImage(models.Model):
    """Image for galleryItem"""
    item = models.ForeignKey(GalleryItem, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery')
    order_of_images = models.IntegerField()

    class Meta:
        ordering = ['order_of_images']

    def __str__(self):
        return f'{self.id} {self.item}'
