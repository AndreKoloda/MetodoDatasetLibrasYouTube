from video import Video
from channel_persistence import ChannelDB

class Channel:
    def __init__(self, channel_id = '', channel_name = None, channel_count = 0) -> None:
        self.channel_id = channel_id
        self.channel_name = channel_name
        self.video_count = channel_count
        self.processing_time = 0,
        self.videos = []
    
    def set_video_count(self, count):
        self.video_count = count

    def set_processing_time(self, processing_time):
        self.processing_time = processing_time
        ChannelDB().set_processing_time(self)

    def set_videos(self, videos):
        for item in videos:
            try:
                video_id = item.replace('https://www.youtube.com/watch?v=','')
                video = Video(video_id = video_id)
                self.videos.append(video)
            except Exception as e:
                print(e)

    def persist_channel(self):
        channel_db = ChannelDB()
        channel_db.add_new_channel(self)

    def update_channel(self):
        channel_db = ChannelDB()
        channel_db.update_channel(self)

    def get_channel(self, channel_id):
        channel_db = ChannelDB()
        channels = channel_db.get_channel(channel_id)        
        for channel in channels:
            print(channel)
            
    def get_all_channel(self):
        channel_db = ChannelDB()
        channels = channel_db.get_all_channel()        
        for channel in channels:
            print(channel)

    def get_channels_ids(self):
        return ChannelDB().get_channels_ids()
    
    def get_channels_not_processed_ids(self):
        return ChannelDB().get_channels_not_processed_ids()

    def persist_videos_in_channel(self, videos_id):
        channel_db = ChannelDB()

        videos = []

        for id in videos_id:
            videos.append(Video(id))

        channel_db.add_videos(self.channel_id, videos)

    def persist_ids(self):
        if (self.video_count > 0):
            channel_db = ChannelDB()
            channel_db.add_videos(self.videos)
        else:
            print("Não existem videos no canal")

    def get_videos_ids(self):
        channel = ChannelDB()
        return channel.get_videos_ids(self.channel_id)

    def set_caption_created(self, video_id, contain):
        channel_db = ChannelDB()
        channel_db.set_caption_created(self.channel_id, video_id, contain)

    def set_caption_generated(self, video_id, contain):
        channel_db = ChannelDB()
        channel_db.set_caption_generated(self.channel_id, video_id, contain)

    def set_duration_video(self, video_id, time):
        channel_db = ChannelDB()
        channel_db.set_duration_video(self.channel_id, video_id, time)

    def insert_yolo_detection_in_video(self, video_id, yolo):
        ChannelDB().insert_yolo_detection_in_video(self.channel_id, video_id, yolo)

    def insert_face_recognition_in_video(self, video_id, face_recognition):
        ChannelDB().insert_face_recognition_in_video(self.channel_id, video_id, face_recognition)

    def get_videos_with_caption(self):
        return ChannelDB().get_videos_with_caption(self.channel_id)

    def get_videos_id_from_download(self):
        return ChannelDB().get_videos_id_from_download(self.channel_id)