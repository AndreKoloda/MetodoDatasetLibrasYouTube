from googleapiclient.discovery import build

youTubeApiKey = "AIzaSyAmopKhTctIFo854CbKCQ17zHiwZbO1SI0"
youtube_api = build('youtube','v3', developerKey= youTubeApiKey)


def get_ids_from_channel(channel_ids_list):
    response_ids = []
    response_items = []
    for channel_id in channel_ids_list:
        next_page_token = None
        i = 1  # retirar depois, usado apenas para limitar a quantidade de resultados
        # Problema que teremos que contornar:
        # The request cannot be completed because you have exceeded your <a href="/youtube/v3/getting-started#quota">quota</a>.". Details: "[{'message': 'The request cannot be completed because you have exceeded your <a href="/youtube/v3/getting-started#quota">quota</a>.', 'domain': 'youtube.quota', 'reason': 'quotaExceeded'}]"
        while True:
            request = youtube_api.search().list(
                    #q={channel_id},
                    part="id",
                    channelId=channel_id,
                    #maxResults=50,
                    pageToken=next_page_token
                )

            response = request.execute()
            response_items += response['items']
            response_ids += (list(map(lambda x: x['id'], response_items)))

            next_page_token = response.get('nextPageToken')
            i += 1
            
            if (i == 12) or (next_page_token is None):  # remover depois todas as ocorrências de i
                break

    return response_ids


def sort_ids_obtained_from_channel(channel_obtained_ids):
    playlists_ids = []
    videos_ids = []
    for obtained_id in channel_obtained_ids:
        if ('videoId' in obtained_id):
            id = obtained_id['videoId']
            videos_ids.append(id)
        elif ('playlistId' in obtained_id):
            id = obtained_id['playlistId']
            playlists_ids.append(id)
    return playlists_ids, videos_ids


def get_video_ids_from_playlist(playlist_ids_list):
    obtained_video_ids = []
    for playlist_id in playlist_ids_list: 
        playlist_videos = []

        while True:
            res = youtube_api.playlistItems().list(part='snippet', playlistId = playlist_id, maxResults=200, pageToken= None).execute()
            playlist_videos += res['items']
            
            nextPage_token = None #res.get('nextPageToken')
            
            if nextPage_token is None:
                break

        obtained_video_ids += list(map(lambda x: x['snippet']['resourceId']['videoId'], playlist_videos))

    return obtained_video_ids

