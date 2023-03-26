# from video import Video
# from channel import Channel as chn
# from recognition import Yolo, FaceRecognition
from channel_persistence import ChannelDB, ChannelStatistic
from videos_download_persistence import VideosResultsDB

videos_id = ChannelDB().get_all_videos_recognized()

VideosResultsDB().persist_videos_afirmative(videos_id)

# teste = ChannelDB().count_channels_processed_time()
# statistics = []
# for id in channel_id:
#     statistics.append(ChannelDB().get_channel_statistic(id))

# channels_results = ChannelStatistic()
# for item in statistics:
#     channels_results.video_count += item.video_count
#     channels_results.video_with_caption += item.video_with_caption
#     channels_results.video_recognized_count += item.video_recognized_count
#     channels_results.yolo_L += item.yolo_L
#     channels_results.yolo_R += item.yolo_R
#     channels_results.face_L += item.face_L
#     channels_results.face_R += item.face_R
#     channels_results.recognized_left += item.recognized_left
#     channels_results.recognized_right += item.recognized_right
#     channels_results.sum_time_video_L += item.sum_time_video_L
#     channels_results.sum_time_video_R += item.sum_time_video_R
#     channels_results.sum_time_video_recognized += item.sum_time_video_recognized

# print(channels_results)


# list_channels = chn().get_channels_ids()
# count_channels = len(list_channels)
# videos_id_download = VideosResultsDB().get_videos_from_download()
# count_videos_id_download = len(videos_id_download)

# print(set(list_channels))

# new_channel = chn('UC1kilS1DdyYOEGItHPRukBw')
# # new_channel.set_video_count(10)
# # new_channel.channel_name = 'teste'
# # new_channel.video_count = 100

# # new_channel.update_channel()

# # chn('UC7PilvJkzxDyuB0Q6p3I4qA').verify_channel_exists()

# # channel_id = chn('123channel').set_duration_video('2','00:20:15.00')

# channels_id = ChannelDB().count_videos_channels()
# teste = VideosResultsDB().get_videos_from_download()
# print(teste)

# # print(len(VideosResultsDB().get_videos_from_download()))


# # recog = chn('UC7PilvJkzxDyuB0Q6p3I4qA').ver()
# # print(recog)


# import requests
# from bs4 import BeautifulSoup

# video_url = '<your-video-url>'
# response = requests.get('https://www.youtube.com/watch?v=sYUVIsHATS0')
# html_content = response.text

# soup = BeautifulSoup(html_content, 'html.parser')
# category_element = soup.find('meta', {'property': 'og:video:category'})

# category = category_element['content']

# from database_connection import MongoDB
# from json_converter import from_dict
# from concurrent.futures import ThreadPoolExecutor, as_completed
# from constants import MAX_WORKERS, ID_FRAME_SEPARATOR, WINDOWS
# import logging
# import datetime

# logging.basicConfig(filename='app.log',level=logging.ERROR)








# # from pytube import Channel
# # channel_url = 'https://www.youtube.com/channel/UC1kilS1DdyYOEGItHPRukBw'
# # channel = Channel(channel_url)
# # teste = channel.channel_url

# from pymongo import MongoClient
# from database_connection import MongoDB
# from json_converter import from_dict

# client = MongoClient().get_database('LibrasDB').get_collection('channels')

# channel = client.insert_many(from_dict(insert))