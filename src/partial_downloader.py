from multiprocessing import cpu_count
from concurrent.futures import ThreadPoolExecutor, as_completed
from pytube import YouTube
from channel import Channel
from constants import MAX_WORKERS, ID_FRAME_SEPARATOR, WINDOWS
import os
import time
import platform

class PartialDownloader():
    def __init__(self, videos_ids, videos_output_path='partial_video_downloads', frames_output_path='frames'):
        self.videos_ids = videos_ids
        self.video_time_info = []
        self.videos_output_path = videos_output_path
        self.frames_output_path = frames_output_path

    def remove_video_id(self, video_id):
        self.videos_ids.remove(video_id)
    
    def _get_video_file_name(self, video_info):
        return f"{video_info['id']}{ID_FRAME_SEPARATOR}{video_info['iteration']}"
    
    def download(self):
        os.makedirs(self.videos_output_path, exist_ok=True)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = {executor.submit(self._download, item): item for item in self.video_time_info}
            for task in as_completed(tasks):
                print(task)

    def _download(self, video_info):         
        video_name = self._get_video_file_name(video_info)
        command_download = f'{self._get_command_start()}ffmpeg -y -ss {video_info["time"]} -t 00:00:00.10 -i $(yt-dlp -vU -f 18 --get-url "https://www.youtube.com/watch?v={video_info["id"]}") -c copy "{self.videos_output_path}/{video_name}.mp4"'
        #print(command_download)
        os.system(command_download)
    
    def set_video_time_info(self, channel_id):
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = {executor.submit(self._set_video_time_info, item, channel_id): item for item in self.videos_ids}
            for task in as_completed(tasks):
                print(task)

    def _set_video_time_info(self, video_id, channel_id):
        try:
            video_duration = YouTube(f'https://www.youtube.com/watch?v={video_id}').length
            Channel(channel_id).set_duration_video(video_id, video_duration)
        except:
            self.remove_video_id(video_id)
            
        for i in range (1,4):
            video_time = time.gmtime(video_duration / 4 * i )
            formatted_time = time.strftime("%H:%M:%S", video_time)
            self.video_time_info.append({'id': video_id, 'time': formatted_time, 'iteration': str(i)})
    
    def get_frames(self):
        os.makedirs(self.frames_output_path, exist_ok=True)

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = {executor.submit(self._get_frames, item): item for item in self.video_time_info}
            for task in as_completed(tasks):
                print(task)

    def _get_frames(self, video_info):
        video_name = self._get_video_file_name(video_info)
        command = f'{self._get_command_start()}ffmpeg -ss 00:00:00.050 -i "{self.videos_output_path}/{video_name}.mp4" -frames:v 1 -q:v 2 "{self.frames_output_path}/{video_name}.jpg"'
        os.system(command)

    def _get_command_start(self):
        if platform.system() == WINDOWS:
            return 'powershell '
        return ''



