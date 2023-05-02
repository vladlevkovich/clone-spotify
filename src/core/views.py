from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import *
from .forms import *
from ..subscriptions.models import *


def index(request):
    """Home page"""
    albums = Album.objects.filter(is_public=True)
    songs = Songs.objects.all()
    data = {
        'albums': albums,
        'songs': songs
    }
    return render(request, 'core/index.html', data)


def get_album(request, album_slug):
    """Album page"""
    user_profile = Profile.objects.get(user=request.user)
    album = get_object_or_404(Album, slug=album_slug)
    songs = list(album.song.all().values())
    is_favorite = False
    print('songs:', songs)

    if user_profile.is_subscription:
        if album.favorite.filter(id=request.user.id).exists():
            is_favorite = True
    else:
        return
    data = {
        'album': album,
        'songs': songs,
        'is_favorite': is_favorite
    }
    return render(request, 'core/album_detail.html', data)


def list_genres(request):
    """List genres"""
    genres = Genre.objects.all()
    context = {
        'genres': genres
    }
    return render(request, 'core/genres.html', context)


@login_required()
def favorite_album(request, album_slug):
    """Favorite album"""
    user_profile = Profile.objects.get(user=request.user)
    if user_profile.is_subscription:
        album = get_object_or_404(Album, slug=album_slug)
        if album.favorite.filter(id=request.user.id).exists():
            album.favorite.remove(request.user)
        else:
            album.favorite.add(request.user)

        return redirect(album.get_absolute_url())
    else:
        return


@login_required()
def create_album(request):
    """Create a new album"""
    user_profile = Profile.objects.get(user=request.user)

    if user_profile.is_subscription:
        if request.method == 'POST':
            form = CreateAlbumForm(request.POST, request.FILES)
            if form.is_valid():
                album = form.save(commit=False)
                album.user = request.user
                # album.cover = request.FILES.get('cover')
                # print('cover:', album.cover)
                album.save()
                form.save_m2m()
                return redirect('/')
        else:
            form = CreateAlbumForm()

        data = {
            'form': form
        }
        return render(request, 'core/create_album.html', data)
    else:
        return render(request, 'core/error.html')


@login_required()
def album_update(request, album_slug):
    user = request.user
    album = Album.objects.get(slug=album_slug)
    user_profile = Profile.objects.get(user=user)

    if user_profile.is_subscription:
        if album.user == user:
            if request.method == 'POST':
                form = CreateAlbumForm(request.POST, request.FILES, instance=album)
                if form.is_valid():
                    form.save()
                    return redirect('album', album_slug=album.slug)
            else:
                form = CreateAlbumForm(instance=album)

            context = {
                'form': form
            }
            return render(request, 'core/update_album.html', context)
        else:
            messages.success(request, 'You cannot edit this composition')
            return redirect('profile')
    else:
        return


@login_required()
def add_song(request):
    """Add song"""
    user_profile = Profile.objects.get(user=request.user)

    if user_profile.is_subscription:
        if request.method == 'POST':
            form = AddSongForm(request.POST, request.FILES)
            if form.is_valid():
                song = form.save(commit=False)
                song.user = request.user
                song.save()
                form.save_m2m()
                return redirect('profile')
        else:
            form = AddSongForm()

        data = {
            'form': form
        }
        return render(request, 'core/add_song.html', data)
    else:
        return HttpResponse("You must have an active subscription to add a song.")


@login_required()
def song_update(request, pk):
    user = request.user
    song = Songs.objects.get(pk=pk)
    user_profile = Profile.objects.get(user=user)

    if user_profile.is_subscription:
        if song.user == user:
            if request.method == 'POST':
                form = AddSongForm(request.POST, request.FILES, instance=song)
                if form.is_valid():
                    form.save()
                    return redirect('profile')
            else:
                form = AddSongForm(instance=song)

            context = {
                'form': form
            }
            return render(request, 'core/update_song.html', context)
        else:
            messages.success(request, 'You cannot edit this composition')
            return redirect('profile')
    else:
        return


@login_required()
def profile(request):
    """Create user profile"""
    user = request.user
    albums = Album.objects.filter(user=user)
    favorite_list = user.favorite_album.all()
    try:
        profile = Profile.objects.get(user=user)
        profile.albums.set(albums)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(
            user=user
        )
        profile.albums.set(albums)
    # print('id:', UserSubscription.objects.get(user=request.user).sub_id)
    # print('email:', request.user.email)

    data = {
        'profile': profile,
        'favorite_list': favorite_list,
        'user': user
    }
    return render(request, 'core/profile.html', data)


@login_required()
def update_profile(request):
    user = request.user
    get_profile = Profile.objects.get(user=user)
    if get_profile:
        if request.method == 'POST':
            form = UpdateProfileForm(request.POST, request.FILES, instance=get_profile)
            if form.is_valid():
                form.save()
                return redirect('profile')
        else:
            form = UpdateProfileForm()
        context = {
            'get_profile': get_profile,
            'update': True,
            'form': UpdateProfileForm(instance=get_profile)
        }
        return render(request, 'core/update_profile.html', context)


def list_singer(request):
    """List of singers"""
    singers = Profile.objects.filter(is_singer=True)
    data = {
        'singers': singers
    }
    return render(request, 'core/singers.html', data)


def get_singer(request, pk):
    """Get a singer"""
    user = request.user
    singer = get_object_or_404(Profile, pk=pk)
    singer_user = singer.user
    singer_album = singer.albums.all()
    current_user = Profile.objects.get(user=user)

    # followers = singer.followers.all()

    if request.user.is_authenticated:
        if request.method == 'POST':
            action = request.POST['follower']

            if action == 'unfollow':
                current_user.followers.remove(singer_user)
            elif action == 'follow':
                current_user.followers.add(singer_user)
            else:
                messages.success(request, 'Error!')
    else:
        messages.success(request, 'Sing in to continue')
        return redirect('login')

    #  print('my_sub:', current_user.followers.all())

    context = {
        'singer': singer,
        'singer_album': singer_album,
        'user': user,
        'current_user': current_user,
        'singer_user': singer_user
    }
    return render(request, 'core/singer.html', context)


def user_list_followers(request, pk):
    """List user's favorite albums"""
    current_user = Profile.objects.get(pk=pk)
    print('pk:', current_user)
    followers_current_user = current_user.followers.all()
    for user in followers_current_user:
        singer = get_object_or_404(Profile, pk=user.id)

    context = {
        'followers_current_user': followers_current_user
    }
    return render(request, 'core/list_followers.html', context)


def search(request):
    """Search album"""
    result = []

    if request.method == 'GET':
        query = request.GET.get('search')
        if query == '':
            query = None

        result = Album.objects.filter(Q(title__icontains=query))
        print('result:', result)

        data = {
            'result': result,
            'query': query
        }
        return render(request, 'core/search.html', data)
