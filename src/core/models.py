from django.db import models
from django.urls import reverse
from slugify import slugify
from datetime import datetime

from config import settings
import uuid


class Genre(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=50)
    slug = models.SlugField(max_length=250, db_index=True, unique=True)

    def __str__(self):
        return self.title


# class Author(models.Model):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
#     first_name = models.CharField(max_length=50, blank=True, null=True)
#     last_name = models.CharField(max_length=50, blank=True)
#     name = models.CharField(max_length=50)
#     country = models.CharField(max_length=25)
#     year_birth = models.DateTimeField(blank=True, null=True)
#
#     def __str__(self):
#         if not self.last_name or self.last_name:
#             return self.name
#         else:
#             return f'{self.first_name} - {self.last_name}'


class Songs(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    genre = models.ForeignKey(Genre, blank=True, null=True, on_delete=models.SET_NULL)
    song = models.FileField(upload_to='songs/')
    release_date = models.DateField(blank=True, null=True)
    slug = models.SlugField(db_index=True, unique=True)

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse('song', kwargs={'song_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug and not self.release_date:
            self.slug = slugify(self.title)
            self.release_date = datetime.now()
        return super().save(*args, **kwargs)


class Album(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    cover = models.ImageField(upload_to='covers/', blank=True, null=True)
    song = models.ManyToManyField(Songs, blank=True)
    favorite = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='favorite_album', default=None, blank=True)
    is_public = models.BooleanField(default=False)
    slug = models.SlugField(db_index=True, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.title}'

    def get_absolute_url(self):
        return reverse('album', kwargs={'album_slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        return super().save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     if Album.objects.filter(title=self.title).exists():
    #         extra = str(randint(1, 10000))
    #         self.slug = slugify(self.title) + "-" + extra
    #     return super(Album, self).save(*args, **kwargs)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    bio = models.CharField(max_length=5000, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True)
    albums = models.ManyToManyField(Album)
    is_singer = models.BooleanField(default=False)
    followers = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='followers')
    is_subscription = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user)

    def get_absolute_url(self):
        return reverse('profile', args=[str(self.pk)])

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return '/static/image/avatar-default.svg'
