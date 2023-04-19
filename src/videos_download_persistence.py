from database_connection import MongoDB
from concurrent.futures import ThreadPoolExecutor, as_completed
from constants import MAX_WORKERS
from json_converter import from_dict


class VideosResultsDB:
    def __init__(self) -> None:
        self.collection = MongoDB().connect_collection('videos')

    def _add_video_affirmative(self, id):
         self.collection.insert_one({'video_id': id})

    def persist_videos_afirmative(self, videos_id):
        l = []
        for i in videos_id:
            if i not in l:
                l.append(i)
        l.sort()
        videos_id = l

        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                tasks = {executor.submit(self._add_video_affirmative, id): id for id in videos_id}
                for task in as_completed(tasks):
                    print(task)

    def get_videos_from_download(self):
        videos = self.collection.find({})
        v = [video["video_id"] for video in videos]
        return v
    