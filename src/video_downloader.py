from pytube import YouTube
from pytube.exceptions import VideoUnavailable, AgeRestrictedError
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from constants import MAX_WORKERS

class VideoDownloader:
    def __init__(self, output_path='videos'):
        self.output_path = output_path

    def download(self, vid_ids):
        print("\nDownloading videos...")
        pbar = tqdm(total=len(vid_ids))

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = {executor.submit(self._download, video_id): video_id for video_id in vid_ids}
            for task in as_completed(tasks):
                pbar.update()
        
        pbar.close()
        print("Video download completed.\n")
    
    def _download(self, video_id):
        try:
            yt = YouTube(f'https://www.youtube.com/watch?v={video_id}')
            yt.check_availability()
            if yt.age_restricted:
                raise AgeRestrictedError(yt.video_id)

            streams = yt.streams.filter(file_extension='mp4')
            streams.get_highest_resolution().download(self.output_path, filename=f'{video_id}.mp4')
        except VideoUnavailable as err:
            print(err)


if __name__ == '__main__':
    pass

