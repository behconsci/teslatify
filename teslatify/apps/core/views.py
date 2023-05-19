import teslapy

from django.shortcuts import render, redirect, reverse


def home(request):

    if not request.user.is_authenticated:
        return redirect(reverse('tesla_login'))

    tesla = teslapy.Tesla(request.user.email)
    if not tesla.authorized:
        # tesla is not authorized. So we need the user to login again via tesla_auth
        return redirect(reverse('tesla_login'))

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
            'song_title': data['vehicle_state']['media_info']['now_playing_title'],
            'is_radio': data['vehicle_state']['media_info']['now_playing_source'] == 12,
            'artist_name': data['vehicle_state']['media_info']['now_playing_artist']
        })

    tesla.close()

    return render(request, 'index.html', {
        'vehicle_data': vehicle_data
    })
