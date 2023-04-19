import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
from constants import MAX_WORKERS
from channel import Channel as chn


def extract_chanel_ids(channel_url_list):
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = {executor.submit(_get_channel_id, channel_url): channel_url for channel_url in channel_url_list}
        for task in as_completed(tasks):
            pass
    
    return chn().get_channels_not_processed_ids()


def _get_channel_id(channel_url):
    try:
        response = requests.get(channel_url)
        soup = BeautifulSoup(response.content, "html.parser")

        channel_id = soup.find("meta", attrs={"itemprop": "channelId"})["content"]

        print(channel_id)
        channel = chn(channel_id)
        channel.persist_channel()
    except Exception as ex:
        print(ex)
