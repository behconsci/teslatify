import teslapy

from django.shortcuts import render, redirect, reverse


def home(request):

    if not request.user.is_authenticated:
        return redirect(reverse('tesla_login'))

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

    return render(request, 'index.html', {
        'vehicle_data': vehicle_data
    })
