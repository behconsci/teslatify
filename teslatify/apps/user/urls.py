from django.urls import path

from teslatify.apps.user.views import (
    tesla_login,
    tesla_auth,
    tesla_auth_complete,

    spotify_login,
    spotify_callback,
    add_to_spotify
)

urlpatterns = [
    path('login/', tesla_login, name='tesla_login'),
    path('tesla/auth/', tesla_auth, name='tesla_auth'),
    path('tesla/auth/complete/', tesla_auth_complete, name='tesla_auth_complete'),

    path('spotify/login/', spotify_login, name='spotify_login'),
    path('spotify/callback/', spotify_callback, name='spotify_callback'),
    path('spotify/add_to_spotify/', add_to_spotify, name='add_to_spotify'),
]
