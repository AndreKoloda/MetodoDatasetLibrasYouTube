from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, NoTranscriptAvailable
from youtube_transcript_api.formatters import JSONFormatter, SRTFormatter
from channel import Channel
from video import Video
from concurrent.futures import ThreadPoolExecutor, as_completed
from constants import MAX_WORKERS, GENERATED, MANUALLY_CREATED, SLICE_SIZE
from tqdm import tqdm
import os


class SubtitleDownloader:
    def __init__(self, languages, output_path='subtitles', get_json=True, get_srt=True):
        self.languages = languages
        self.output_path = output_path
        self.get_json = get_json
        self.get_srt = get_srt
    
    def sort_transcripts(self, channel_id, video_id):
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            video = Video(video_id)

            try:
                Channel(channel_id).set_caption_created(video_id, transcript_list.find_manually_created_transcript(self.languages) != '')
            except NoTranscriptFound:
                pass
            
            try:
                Channel(channel_id).set_caption_generated(video_id, transcript_list.find_generated_transcript(self.languages) != '')
            except NoTranscriptFound:
                pass
                    
        except (TranscriptsDisabled, NoTranscriptAvailable):
            pass

    def filter_only_having_transcripts(self, channel_id):
        vid_ids = Channel(channel_id).get_videos_ids()
        filtered_videos = vid_ids.copy()
        print("\nFiltering transcripts...")

        slices = [(vid_ids[i:i+SLICE_SIZE]) for i in range(0, len(vid_ids), SLICE_SIZE)]
        pbar = tqdm(total=len(vid_ids))

        for video_ids in slices:
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                tasks = {executor.submit(self.sort_transcripts, channel_id, video_id): video_id for video_id in video_ids}
                for task in as_completed(tasks):
                    pbar.update()

        pbar.close()
        print('Transcripts filtering completed.')

        filtered_videos = Channel(channel_id).get_videos_with_caption()
        return filtered_videos
    
    def download(self, vid_ids):
        print("\nDownloading transcripts...")
        pbar = tqdm(total=len(vid_ids))

        slices = [(vid_ids[i:i+SLICE_SIZE]) for i in range(0, len(vid_ids), SLICE_SIZE)]

        for video_ids in slices:
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                tasks = {executor.submit(self._download, video_id): video_id for video_id in video_ids}
                for task in as_completed(tasks):
                    pbar.update()
        
        pbar.close()
        print("Transcripts download completed.\n")

    def _download(self, video_id):
        try:
            subtitle_list = YouTubeTranscriptApi.list_transcripts(video_id)

            self._download_subtitle(subtitle_list)
            self._download_subtitle(subtitle_list, True)

        except Exception as e:
            print(e)
        except (TranscriptsDisabled, NoTranscriptAvailable):
            return

    def _download_subtitle(self, subtitle_list, manually_created=False):
        try:
            if manually_created:
                subtitle = subtitle_list.find_manually_created_transcript(self.languages)
            else:
                subtitle = subtitle_list.find_generated_transcript(self.languages)
        except NoTranscriptFound:
            return

        if self.get_json:
            self._generate_json(subtitle)
        
        if self.get_srt:
            self._generate_srt(subtitle)

    def _generate_json(self, subtitle):
        formatter = JSONFormatter()
        json_formatted = formatter.format_transcript(subtitle.fetch(), indent=2, ensure_ascii=False)
        self._generate_file(subtitle, 'json', json_formatted)

    def _generate_srt(self, subtitle):
        formatter = SRTFormatter()
        srt_formatted = formatter.format_transcript(subtitle.fetch()) 
        self._generate_file(subtitle, 'srt', srt_formatted)

    def _generate_file(self, subtitle, format, formatted_sub):
        if subtitle.is_generated:
            generated_or_manual = GENERATED
        else:
            generated_or_manual = MANUALLY_CREATED

        path = f'{self.output_path}/{generated_or_manual}/'

        if self.get_srt and self.get_json:
            path += f'{format}/'

        os.makedirs(path, exist_ok=True)
        
        path += f'{subtitle.video_id}.{format}'

        with open(path, 'w', encoding='utf-8') as file:
            file.write(formatted_sub)


if __name__ == '__main__':
    pass
