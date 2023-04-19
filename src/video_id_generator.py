from pytube import Channel
from channel import Channel as chn
from concurrent.futures import ThreadPoolExecutor, as_completed
from pytube.exceptions import PytubeError
from constants import MAX_WORKERS


def get_video_ids():
    channel_ids = chn('').get_channels_not_processed_ids()
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = {executor.submit(_get_video_ids, channel_url): channel_url for channel_url in channel_ids}
        for task in as_completed(tasks):
            pass


def _get_video_ids(channel_id):
    try:
        channel_url = 'https://www.youtube.com/channel/' + channel_id
        channel = Channel(channel_url)

        channel_obj = chn(channel_id, channel.channel_name, len(channel.video_urls))
        channel_obj.update_channel()

        print(f"Getting video Ids from channel: {channel_url}...")
        print(f"{channel_url}: {len(channel.video_urls)} videos")

        videos_id = [link.replace('https://www.youtube.com/watch?v=', '') for link in channel.video_urls]
        channel_obj.persist_videos_in_channel(videos_id)
        
    except PytubeError as err:
        print(err)
        get_video_url(channel_url)
