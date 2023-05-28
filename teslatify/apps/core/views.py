import teslapy
import spotipy

from django.shortcuts import render, redirect, reverse
from django.conf import settings


def home(request):
    if not request.user.is_authenticated:
        return redirect(reverse('tesla_login'))

    # ask user to subscribe if they don't have active subscription
    if not request.user.has_active_subscription():
        return redirect(reverse('start_trial'))

    tesla = teslapy.Tesla(request.user.email)
    if not tesla.authorized:
        token = tesla.refresh_token(refresh_token=request.user.tesla_refresh_token)
        # save the access token and refresh token in the database
        request.user.tesla_access_token = token['access_token']
        request.user.tesla_refresh_token = token['refresh_token']
        request.user.save()

    vehicle_data = []
    vehicles = tesla.vehicle_list()
    for vehicle in vehicles:
        if not vehicle.available():
            vehicle.sync_wake_up()

        data = vehicle.get_vehicle_data()
        # turn data to dict
        data = dict(data)

        vehicle_data.append({
            'display_name': data['display_name'],
            'vehicle_id': data['vehicle_id'],
            'song_title': data.get('vehicle_state').get('media_info').get('now_playing_title', ''),
            'artist_name': data.get('vehicle_state').get('media_info').get('now_playing_artist', ''),
        })

    tesla.close()

    # check if user's spotify account is connected, then
    # check if access token is expired, then refresh it.
    if request.user.spotify_access_token:
        sp = spotipy.Spotify(auth=request.user.spotify_access_token)
        try:
            sp.current_user()
        except spotipy.exceptions.SpotifyException:
            # access token is expired
            spotify_auth_manager = spotipy.oauth2.SpotifyOAuth(
                client_id=settings.SPOTIFY_CLIENT_ID,
                client_secret=settings.SPOTIFY_CLIENT_SECRET,
                redirect_uri=settings.SPOTIFY_REDIRECT_URI,
                scope=settings.SPOTIFY_SCOPES,
            )
            token = spotify_auth_manager.refresh_access_token(request.user.spotify_refresh_token)
            request.user.spotify_access_token = token['access_token']
            request.user.save()

    return render(request, 'index.html', {
        'vehicle_data': vehicle_data
    })
