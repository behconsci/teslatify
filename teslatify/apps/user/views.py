from typing import Tuple
from requests_oauthlib import OAuth2Session

import spotify
import teslapy


from django.shortcuts import render, redirect, reverse
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import login

from teslatify.apps.user.models import User


def tesla_login(request):
    """ it only asks for email address """

    if not request.user.is_authenticated:
        return render(request, 'login.html')

    return redirect(reverse('home'))


def tesla_auth(request):
    """ if user is not logged in, it redirects to tesla auth page """

    # if not post request, return error
    if request.method != 'POST':
        return JsonResponse({
            'error': 'Only POST method is allowed'
        }, status=405)

    email = request.POST.get('email')
    if not email:
        return JsonResponse({
            'error': 'Email is required'
        }, status=400)

    if not request.user.is_authenticated:
        tesla = teslapy.Tesla(email)
    else:
        tesla = teslapy.Tesla(request.user.email)

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
    """ it receives auth_url from POST. This happens usually only once. """

    if request.method != 'POST':
        return JsonResponse({
            'error': 'Only POST method is allowed'
        }, status=405)

    # get the auth_url from the request
    auth_url = request.POST.get('auth_url')
    state = request.POST.get('state')
    code_verifier = request.POST.get('code_verifier')
    email = request.POST.get('email')

    # call tesla API to get the access token and refresh token
    tesla = teslapy.Tesla(email, state=state, code_verifier=code_verifier)
    if not tesla.authorized:

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


def spotify_login(request):
    """ it redirects to spotify login page """

    # check if user is logged in. This never happens, but just in case
    if not request.user.is_authenticated:
        return redirect(reverse('home'))

    oauth2_scopes: Tuple[str, str] = (
        'user-modify-playback-state',
        'user-read-playback-state'
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
    oauth2_scopes: Tuple[str, str] = (
        'user-modify-playback-state',
        'user-read-playback-state'
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
    user.save()

    # redirect to index page
    return redirect(reverse('home'))


def add_to_spotify(request):
    """
    Adds a song to the user's spotify playlist. It calls spotify API to add the song.
    """

    # call spotify API to add the song
    song_title = request.GET.get('song_title')
    artist_name = request.GET.get('artist_name')

    spotify_client = spotify.Client(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET
    )
    playlist = spotify.Playlist(client=spotify_client)
    found_songs = spotify_client.search(song_title, types=['track'])
    print(found_songs)

    # return json response
    return JsonResponse({'success': True}, status=200)

