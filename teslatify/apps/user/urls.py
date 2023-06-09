from django.urls import path
from django.contrib.auth.views import LogoutView

from teslatify.apps.user.views import (
    start_trial_page,
    trial_started_callback,
    tesla_login,
    tesla_auth,
    tesla_auth_complete,

    profile_page,
    delete_profile,
    disconnect_spotify,

    spotify_login,
    spotify_callback,
    add_to_spotify
)

urlpatterns = [
    path('login/', tesla_login, name='tesla_login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # add start_trial_page
    path('start_trial/', start_trial_page, name='start_trial'),

    # profile page
    path('profile/', profile_page, name='profile'),
    path('profile/delete/', delete_profile, name='delete_profile'),
    path('profile/disconnect_spotify/', disconnect_spotify, name='disconnect_spotify'),

    path('trial-started-callback/', trial_started_callback, name='trial_started_callback'),

    path('tesla/auth/', tesla_auth, name='tesla_auth'),
    path('tesla/auth/complete/', tesla_auth_complete, name='tesla_auth_complete'),

    path('spotify/login/', spotify_login, name='spotify_login'),
    path('spotify/callback/', spotify_callback, name='spotify_callback'),
    path('spotify/add_to_spotify/', add_to_spotify, name='add_to_spotify'),
]
