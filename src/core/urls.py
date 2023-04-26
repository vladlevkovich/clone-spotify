from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *


urlpatterns = [
    path('', index, name='home'),
    path('album/<str:album_slug>/', get_album, name='album'),

    path('genres/', list_genres, name='genres'),

    path('add-favorite-album/<str:album_slug>/', favorite_album, name='favorite'),

    path('create-album/', create_album, name='create_album'),
    path('album-update/<str:album_slug>/', album_update, name='album_update'),

    path('add-song/', add_song, name='add_song'),
    path('update-song/<uuid:pk>/', song_update, name='song_update'),

    path('profile/', profile, name='profile'),
    path('profile-update/', update_profile, name='update_profile'),
    path('profile/list-followers/<int:pk>/', user_list_followers, name='user_followers'),

    path('search/', search, name='search'),

    path('singers/', list_singer, name='singers'),
    path('singer/<int:pk>/', get_singer, name='singer'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
