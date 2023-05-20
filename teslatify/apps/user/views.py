from typing import Tuple
from requests_oauthlib import OAuth2Session

import spotify
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import teslapy

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import login

from teslatify.apps.user.models import User


def tesla_login(request):
    """ it only asks for email address """

    # if user opens the login page while logged in, redirect to home page
    if request.user.is_authenticated:
        return redirect(reverse('home'))

    # it asks for email address and redirects to tesla_auth with POST request to get the auth_url
    return render(request, 'login.html')


def tesla_auth(request):
    """ it receives email address from POST, generates auth_url and redirects to tesla_auth_complete """

    # if not post request, return error
    if request.method != 'POST':
        return render(request, 'login.html', {
            'error': 'Only POST method is allowed'
        }, status=405)

    email = request.POST.get('email')
    if not email:
        return render(request, 'login.html', {
            'error': 'Email is required'
        }, status=400)

    tesla = teslapy.Tesla(email)

    if not tesla.authorized:
        state = tesla.new_state()
        code_verifier = tesla.new_code_verifier()

        # no idea why I have to decode and encode it back
        code_verifier = code_verifier.decode('utf-8')
        auth_url = tesla.authorization_url(
            state=state,
            code_verifier=code_verifier.encode('utf-8'),
        )

        return render(request, 'login.html', {
            'email': email,
            'auth_url': auth_url,
            'state': state,
            'code_verifier': code_verifier
        })

    else:
        # tesla is authorized.
        # check if user exists in the database with the given email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # create a new user
            user = User.objects.create_user(username=email, email=email)
            user.save()

        # login the user
        login(request, user)

        return redirect(reverse('home'))


def tesla_auth_complete(request):
    """
    it receives auth_url from POST and tries to get the access token and refresh token from tesla API.
    This happens only once when the user logs in for the first time.
    """

    if request.method != 'POST':
        return render(request, 'login.html', {
            'error': 'Only POST method is allowed'
        }, status=405)

    # get the auth_url from the request
    auth_url = request.POST.get('auth_url')
    state = request.POST.get('state')
    code_verifier = request.POST.get('code_verifier')
    email = request.POST.get('email')

    # call tesla API to get the access token and refresh token
    tesla = teslapy.Tesla(email=email, state=state, code_verifier=code_verifier)
    token = tesla.fetch_token(authorization_response=auth_url)
    # check if user exists in the database with the given email
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        # create a new user
        user = User.objects.create_user(username=email, email=email)
        user.save()

    # login the user
    login(request, user)

    # save the access token and refresh token in the database
    user.tesla_access_token = token['access_token']
    user.tesla_refresh_token = token['refresh_token']
    user.save()

    # redirect to index page if tesla is authorized
    return redirect(reverse('home'))


@login_required
def spotify_login(request):
    """ it redirects to spotify login page """

    oauth2_scopes = (
        'playlist-read-private',
        'playlist-read-collaborative',
        'playlist-modify-private',
        'playlist-modify-public'
    )
    oauth2: spotify.OAuth2 = spotify.OAuth2(
        settings.SPOTIFY_CLIENT_ID,
        settings.SPOTIFY_REDIRECT_URI,
        scopes=oauth2_scopes,
        state=request.user.email
    )

    auth_url: str = oauth2.url
    return redirect(auth_url)


def spotify_callback(request):
    """ it handles the callback from spotify API and saves the access token and refresh token in the database """
    # get the code from the request
    code = request.GET.get('code')
    state = request.GET.get('state')

    # call spotify API to get the access token and refresh token
    oauth2_scopes = (
        'playlist-read-private',
        'playlist-read-collaborative',
        'playlist-modify-private',
        'playlist-modify-public'
    )
    oauth2 = OAuth2Session(
        settings.SPOTIFY_CLIENT_ID,
        scope=oauth2_scopes,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI
    )

    token = oauth2.fetch_token(
        settings.SPOTIFY_TOKEN_URL,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        code=code
    )
    # save the access token and refresh token in the database

    if not request.user.is_authenticated:
        user = User.objects.get(email=state)
        login(request, user)
    else:
        user = request.user

    user.spotify_access_token = token['access_token']
    user.spotify_refresh_token = token['refresh_token']

    # get spotify user id as well
    sp = spotipy.Spotify(auth=token['access_token'])
    spotify_user = sp.me()
    user.spotify_id = spotify_user['id']
    user.save()

    # redirect to index page
    return redirect('%s?%s' % (reverse('home'), 'spotify_login=success'))


@login_required
def add_to_spotify(request):
    """
    Adds a song to the user's spotify playlist. It calls spotify API to add the song.
    """

    # call spotify API to add the song
    song_title = request.POST.get('song_title')
    artist_name = request.POST.get('artist_name')

    auth_manager = SpotifyClientCredentials(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET
    )
    sp = spotipy.Spotify(auth_manager=auth_manager, auth=request.user.spotify_access_token)

    # check if playlist "Teslatify" exists
    playlists = sp.user_playlists(request.user.spotify_id)
    teslatify_playlist = None
    while playlists:
        for playlist in playlists['items']:
            if playlist['name'] == 'Teslatify':
                teslatify_playlist = playlist
                break
        if teslatify_playlist:
            break

        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None

    if not teslatify_playlist:
        # create a new playlist
        teslatify_playlist = sp.user_playlist_create(request.user.spotify_id, 'Teslatify')

    # add the song to the playlist
    song = sp.search(q='artist:' + artist_name + ' track:' + song_title, type='track')
    if song['tracks']['items']:
        # add only if not already in the playlist
        sp.playlist_replace_items(teslatify_playlist['id'], [song['tracks']['items'][0]['uri']])

    # return json response
    return JsonResponse({'success': True}, status=200)
