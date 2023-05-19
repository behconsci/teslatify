from django.contrib import admin
from django.urls import path, include

from teslatify.apps.core.views import home

urlpatterns = [
    path('', home, name='home'),
    path('user/', include('teslatify.apps.user.urls')),
    path('admin/', admin.site.urls),
]
