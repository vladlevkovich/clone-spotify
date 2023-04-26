from django.contrib import admin
from django.utils.text import slugify
from .models import *


# @admin.register(Author)
# class AuthorAdmin(admin.ModelAdmin):
#     list_display = ('id', 'first_name', 'last_name', 'name')
#     list_filter = ('id',)


@admin.register(Songs)
class SongsAdmin(admin.ModelAdmin):
    list_display = ('id','title', 'release_date')
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'is_public')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}

    # def save_model(self, request, obj, form, change):
    #     if not obj.id:
    #         obj.slug = slugify(str(obj.id))
    #     super().save_model(request, obj, form, change)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', )
    prepopulated_fields = {'slug': ('title',)}


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user')
