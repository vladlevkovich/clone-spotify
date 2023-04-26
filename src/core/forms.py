from django import forms
from slugify import slugify
from .models import *


class CreateAlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ('title', 'cover', 'song', 'is_public')


class AlbumUpdateForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ('title', 'cover', 'song')


class AddSongForm(forms.ModelForm):
    class Meta:
        model = Songs
        fields = ('title', 'genre', 'song')


class UpdateProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('bio', 'avatar')

