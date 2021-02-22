from django.shortcuts import render, redirect
from spotify.credentials import CLIENT_SECRET, CLIENT_ID, REDIRECT_URI
from rest_framework.views import APIView
import requests
from rest_framework import status
from rest_framework.response import Response
from api.models import Room 
from spotify.models import Vote
import json
from .utils import *

from spotify.serializers import SearchSerializer, AddSongSerializer


# Create your views here.

class AuthURL(APIView):
    def get(self,request):
        scopes = 'user-read-playback-state user-modify-playback-state user-read-currently-playing streaming user-read-email user-read-private'
        url = requests.Request('GET','https://accounts.spotify.com/authorize', params={
            'scope':scopes,
            'response_type':'code',
            'redirect_uri':REDIRECT_URI,
            'client_id':CLIENT_ID,
            'show_dialog':True,
          
        }).prepare().url
        print("auth_URl generated")
            
        return Response({'url':url},status=status.HTTP_200_OK)



def spotify_callback(request,format=None):
    code = request.GET.get('code')
    error = request.GET.get('error')
    
    response = requests.post("https://accounts.spotify.com/api/token" , data = {'grant_type':'authorization_code',
        'code':code,
        'redirect_uri':REDIRECT_URI,
        'client_id':CLIENT_ID,
        'client_secret':CLIENT_SECRET,
        'show_dialog':True
    
    } ).json()
    print('spotify_callback : response',response)
    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    if not request.session.exists(request.session.session_key):
        request.session.create()

    update_or_create_user_tokens(request.session.session_key,access_token,token_type,expires_in,refresh_token)

    return redirect('frontend:')


class IsAuthenticated(APIView):
    def get(self,request,format=None):
        is_authenticated = is_spotify_authenticated(self.request.session.session_key)
        
        return Response({'status':is_authenticated}, status=status.HTTP_200_OK)


class CurrentSong(APIView):

    def update_room_song(self,room,song_id):
        current_song = room.current_song
        if current_song != song_id:
            room.current_song = song_id
            room.save(update_fields=['current_song'])
            votes = Vote.objects.filter(room=room).delete()



    def get(self,request,format=None):

        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room  = room[0]
        else:
            return Response({"Bad Request":"Room not found"},status=status.HTTP_404_NOT_FOUND)
        host = room.host

        #get token corresponding to this host/room

        endpoint = "player/currently-playing"

        response = execute_spotify_request(host, endpoint)

        # print(response)

        if 'error' in response or 'item' not in response:
            return Response({"error":"No content"},status=status.HTTP_204_NO_CONTENT)
        
        item = response.get('item')
        duration = item.get('duration_ms')
        progress = response.get('progress_ms')
        album_cover = item.get('album').get('images')[0].get('url')
        is_playing = response.get('is_playing')
        song_id = item.get('id')
        artist_string = ""

        for i, artist in enumerate(item.get('artists')):
            if i>0:
                artist_string += ", "
            name = artist.get('name')
            artist_string += name

        votes = len(Vote.objects.filter(room=room,song_id = song_id))


        song = {
            'title':item.get('name'),
            'artist':artist_string,
            'duration':duration,
            'time': progress,
            'image_url': album_cover,
            'is_playing':is_playing,
            'votes' : votes,
            'votes_required':room.votes_to_skip,
            'id':song_id
        }
        self.update_room_song(room,song_id)

        return Response(song,status=status.HTTP_200_OK)


class PauseSong(APIView):

    def put(self, response, format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]

        if self.request.session.session_key == room.host or room.guest_can_pause:
            pause_song(room.host)
            return Response({},status=status.HTTP_204_NO_CONTENT)
        return Response({},status=status.HTTP_403_FORBIDDEN)


class PlaySong(APIView):
    def put(self,response,format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]

        if self.request.session.session_key ==room.host or room.guest_can_pause:
            play_song(room.host)
            return Response({},status=status.HTTP_204_NO_CONTENT)

        return Response({},status=status.HTTP_403_FORBIDDEN)


class SkipSong(APIView):
    def post(self,request,format=None):

        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)[0]
        votes = Vote.objects.filter(room=room,song_id=room.current_song)
        votes_needed = room.votes_to_skip

        if self.request.session.session_key == room.host or len(votes) +1 >= votes_needed:
            votes.delete()
            skip_song(room.host)
        else:
            vote = Vote(user=self.request.session.session_key,
                        room=room,song_id = room.current_song)
            vote.save()

        return Response({},status=status.HTTP_204_NO_CONTENT)


class GetDevices(APIView):
    def get(self,request,format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)

        if room.exists():
            room = room[0]
        else:
            return Response({"Bad Request":"Room not FOund"},status=status.HTTP_404_NOT_FOUND)
        host = room.host

        response = get_available_devices(host)
        devices = {}

        for device in response.get('devices'):
            name = device.get('name')
            device_id = device.get('id')
            is_active = device.get('is_active')

            devices[device_id] = [name,device_id,is_active]

        return Response(devices,status=status.HTTP_200_OK)


        


        


class SearchSong(APIView):
    print("Search song")

    serializer_class = SearchSerializer

    def post(self,request,format=None):

        room_code = self.request.session.get('room_code')
        # room_code = 'TZUQFM'
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({"Bad Request":"Room not found"},status=status.HTTP_404_NOT_FOUND)
        host = room.host

        
        BASE_URL = "https://api.spotify.com/v1/"
        endpoint = "search"

        tokens = get_user_token(host)
        headers = {'Content-Type': 'application/json',
               'Authorization': "Bearer " + tokens.access_token}
        
       
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
         

            query = serializer.data.get('query')
            query_type = serializer.data.get('query_type')
            if len(query_type) ==0 :
                query_type = ['track']

            query_object = {"q":query,
                            "type":query_type,
                            "limit":10,
                            "market":"IN"}
            
            response = get(BASE_URL + endpoint, query_object,headers=headers).json()
            # with open("D:/newfile.json",'w') as f:
            #     f.write(json.dumps(response.json()))
            track_list = {"list":[]}
            tracks = response.get('tracks')['items']
            for track_obj in tracks:
                final_object = {
                    'song_name' : track_obj['name'],
                    'song_id' : track_obj['id'],
                    'type_of' : track_obj['type'],
                    'track_uri' : track_obj['uri']
                    }
                track_list['list'].append(final_object)
                
              
            # print(type(tracks),len(tracks))
            


            # print(track_list)
            return Response(track_list,status=status.HTTP_200_OK)
            
        return Response({},status=status.HTTP_204_NO_CONTENT)

        # return Response({},status=status.HTTP_200_OK)


class AddSongToQueue(APIView):
    serializer_class = AddSongSerializer

    def post(self,request,format=None):
        room_code = self.request.session.get('room_code')
        room = Room.objects.filter(code=room_code)
        if room.exists():
            room = room[0]
        else:
            return Response({"Bad Request":"Room not Found"},status=status.HTTP_404_NOT_FOUND)

        host = room.host
        BASE_URL = "https://api.spotify.com/v1/me/"
        endpoint = "player/queue"

        tokens = get_user_token(host)
        headers = {'Content-Type': 'application/json',
               'Authorization': "Bearer " + tokens.access_token} 

        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():

            device_id = serializer.data.get('device_id')
            song_uri = serializer.data.get('song_uri')

            headers['uri'] = song_uri
            headers['device_id'] = device_id

            query_object = {'uri':song_uri,
                            'device_id': device_id,
                            }
            url = BASE_URL + endpoint + "?" + f"uri={song_uri}" + f"&device_id={device_id}"
            response = requests.post(url,headers=headers)
            
            return Response(response,status=status.HTTP_200_OK)
        else:
            return Response({"bad requet":"NOT OK"},status=status.HTTP_204_NO_CONTENT)

        




        






