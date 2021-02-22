from django.urls import path
from spotify.views import *
urlpatterns = [
    path('get-auth-url',AuthURL.as_view(),),
    path('redirect',spotify_callback),
    path('is-authenticated',IsAuthenticated.as_view(),),
    path("current-song",CurrentSong.as_view(),),
    path('pause-song',PauseSong.as_view(),),
    path('play-song',PlaySong.as_view(),),
    path('skip-song',SkipSong.as_view(),),
    path('search',SearchSong.as_view(),),
    path("devices",GetDevices.as_view(),),
    path('add-song',AddSongToQueue.as_view(),),

]