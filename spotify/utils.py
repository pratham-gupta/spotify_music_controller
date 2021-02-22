
from .models import SpotifyToken
from django.utils import timezone
from datetime import timedelta
from spotify.credentials import CLIENT_ID, CLIENT_SECRET
from requests import Request, post, get, put


BASE_URL = "https://api.spotify.com/v1/me/"



def get_user_token(session_id):
    user_tokens = SpotifyToken.objects.filter(user=session_id)
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None




def update_or_create_user_tokens(session_id, access_token, token_type, expires_in, refresh_token):
    tokens = get_user_token(session_id)
    print("expires_in",expires_in)
    expires_in =  timezone.now() + timedelta(seconds=expires_in)

    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.expires_in = expires_in
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token','refresh_token','expires_in','token_type'])
    else:
        tokens = SpotifyToken(user=session_id, access_token=access_token, refresh_token=refresh_token, expires_in=expires_in, token_type=token_type)
        tokens.save()
    
def refresh_spotify_token(session_id):
    tokens = get_user_token(session_id)

    refresh_token = tokens.refresh_token
    response = post('https://accounts.spotify.com/api/token',data = {
        'grant_type': 'refresh_token',
        'refresh_token':refresh_token,
        'client_id': CLIENT_ID,
        'client_secret':CLIENT_SECRET,
    }).json()
    # print("refresh response",response)

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')

    # acc to spotify api, refresh token may or may not be returned in response, 
    # if new refresh_token is found, we'll update it else use older one.

    if "refresh_token" in response:
        refresh_token = response.get('refresh_token')
    else:
        refresh_token = refresh_token
    

    update_or_create_user_tokens(session_id,access_token,token_type,expires_in,refresh_token)


 

def is_spotify_authenticated(session_id):
    tokens = get_user_token(session_id)
    # print(tokens)
    # print(tokens)
    # refresh_spotify_token(session_id)
    if tokens != None:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            refresh_spotify_token(session_id)
        return True


    return False




def execute_spotify_request(session_id,endpoint, post_ = False, put_ = False):

    tokens = get_user_token(session_id)
    # print("spotify request",tokens.access_token)
  
  
    headers = {'Content-Type': 'application/json',
               'Authorization': "Bearer " + tokens.access_token}

    if post_:
        response = post(BASE_URL + endpoint, headers=headers)
        # print("skip",response.json())
    if put_:
        response = put(BASE_URL + endpoint, headers=headers)
        # print(response)
        # try:
        #     # print("put request",response.json())
        # except:
        #     pass         
    else:
        response = get(BASE_URL + endpoint, {}, headers=headers)
    
    # print("text",response.url)
    try:
        return response.json()
    except:
        return {'Error': 'Empty response returned, no song playing'}



def play_song(session_id):
    return execute_spotify_request(session_id,"player/play",put_=True)

def pause_song(session_id):
    return execute_spotify_request(session_id,"player/pause",put_=True)


def skip_song(session_id):
    return execute_spotify_request(session_id,"player/next",post_=True)

def get_available_devices(session_id):
    return execute_spotify_request(session_id,"player/devices")
    

def add_song_to_queue(session_id,song_uri,device_id):
    endpoint = 'player/queue'
    token = get_user_token(session_id)
    headers = {'Content-Type': 'application/json',
               'Authorization': "Bearer " + tokens.access_token,
               'device_id':device_id,
               'uri':song_uri}

    response = post(BASE_URL + endpoint,headers=headers)

    try:
        return response.json()
    except:
        return {"Error":"Could not add song to queue."}

    

