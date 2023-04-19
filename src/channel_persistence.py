from database_connection import MongoDB
from json_converter import from_dict
from concurrent.futures import ThreadPoolExecutor, as_completed
from constants import MAX_WORKERS, ID_FRAME_SEPARATOR, MIN_FR_DETECTIONS, MIN_YOLO_DETECTIONS, WINDOWS
import logging
import datetime

logging.basicConfig(filename='app.log',level=logging.ERROR)


class ChannelDB:
    def __init__(self):
        self.db = MongoDB()
        self.channel = self.db.connect_collection('channels')

    def exception_message(e, message = ''):
        logging.error('\n ---- ' + datetime.datetime.now() + ' ---- MongoDB Persistence exception: ' + message + ' \n' + e)

    def add_new_channel(self, channel):
        try:
            if (not self.verify_channel_exists(channel.channel_id)):
                self.channel.insert_one(from_dict(channel))
        except Exception as e:
            message = 'add_new_channel("' +  channel.channel_id + '")'
            self.exception_message(e, message)

    def set_processing_time(self, channel):
        try:
            filter = {'channel_id': channel.channel_id}
            update = {'$set':{'processing_time':channel.processing_time}}
            self.channel.update_one(filter, update)
        except Exception as e:
            message = 'set_processing_time(' +  channel + ')'
            self.exception_message(e, message)


    def update_channel(self, channel):
        try:
            filter = {'channel_id': channel.channel_id}
            update = {'$set':{'channel_name': channel.channel_name, 'video_count': channel.video_count}}
            teste = self.channel.update_one(filter, update)
            print(teste)
        except Exception as e:
            message = 'update_channel("' +  channel.channel_id + '")'
            self.exception_message(e, message)

    def verify_channel_exists(self, channel_id):
        try:
            filter = {'channel_id': channel_id}
            projection = {'_id': 0, 'channel_id': 1}

            result = self.channel.find(filter, projection)

            for doc in result:
                return True
            
            return False
        except Exception as e:
            message = 'verify_channel_exists("' +  channel_id + '")'
            self.exception_message(e, message)

    def get_channel(self, channel_id):
        try:
            return self.channel.find({'channel_id': channel_id})
        except Exception as e:
            message = 'get_channel("' +  channel_id + '")'
            self.exception_message(e, message)

    def get_all_channel(self):
        try:
            return self.channel.find()
        except Exception as e:
            message = 'get_all_channel()'
            self.exception_message(e, message)

    def get_channels_not_processed_ids(self):
        try:
            cursor = self.channel.find({"processing_time": {"$lte": 0}})
            channel_ids = [doc["channel_id"] for doc in cursor]
            return channel_ids
        except Exception as e:
            message = 'get_channels_ids()'
            self.exception_message(e, message)

    def get_channels_ids(self):
        try:
            request = self.channel.find({}, {'channel_id': 1, '_id': 0})
            channel_ids = [iten["channel_id"] for iten in request]
            return channel_ids
        except Exception as e:
            message = 'get_channels_ids()'
            self.exception_message(e, message)

    def get_videos_ids(self, channel_id):
        try:
            query = {"channel_id": channel_id}
            projection = {"videos.video_id": 1, "_id": 0}
            results = self.channel.find(query, projection)

            # Extract the video IDs from the results and store them in a list
            video_ids = [video["video_id"] for result in results for video in result["videos"]]

            # Print the list of video IDs
            return video_ids
        except Exception as e:
            message = 'get_videos_ids("' + channel_id + '")'
            self.exception_message(e, message)

    def add_videos(self, channel_id, videos):
        try:
            query = {'channel_id': channel_id}
            update = {'$set': {'videos': from_dict(videos)}}
            self.channel.update_one(query, update)
        except Exception as e:
            message = 'add_videos("' + channel_id + '", Videos)'
            self.exception_message(e, message)
    
    def set_caption_generated(self, channel_id, video_id, value):
        try:
            query = {"channel_id": channel_id, "videos.video_id": video_id}
            update = {"$set": {"videos.$.caption_generated": value}}
            self.channel.update_one(query, update)
        except Exception as e:
            message = 'set_caption_generated("' + channel_id + '","' +  video_id + ')'
            self.exception_message(e, message)
    
    def set_caption_created(self, channel_id, video_id, value):
        try:
            query = {"channel_id": channel_id, "videos.video_id": video_id}
            update = {"$set": {"videos.$.caption_created": value}}
            self.channel.update_one(query, update)
        except Exception as e:
            message = 'set_caption_created("' + channel_id + '","' +  video_id + ')'
            self.exception_message(e, message)

    def set_duration_video(self, channel_id, video_id, time):
        try:
            query = {"channel_id": channel_id, "videos.video_id": video_id}
            update = {"$set": {"videos.$.duration": time}}
            self.channel.update_one(query, update)
        except Exception as e:
            message = 'set_caption_created("' + channel_id + '","' +  video_id + '",' + time + ')'
            self.exception_message(e, message)

    def insert_yolo_detection_in_video(self, channel_id, video_id, yolo):
        try:
            query = {"channel_id": channel_id, "videos.video_id": video_id, 
                    "$or": [{"videos.detection.yolo.index": {"$ne": yolo.index}}, {"videos.detection.yolo": []}]}
            update = {"$push": {"videos.$.detection.yolo": from_dict(yolo)}}
            self.channel.update_one(query, update)
        except Exception as e:
            message = 'insert_yolo_detection_in_video("' + channel_id + '","' +  video_id + '",' + yolo + ')'
            self.exception_message(e, message)

    def insert_face_recognition_in_video(self, channel_id, video_id, face_recognition):
        try:
            query = {"channel_id": channel_id, "videos.video_id": video_id,
                    "$or": [{"videos.detection.face_recognition.index": {"$ne": face_recognition.index}}, {"videos.detection.face_recognition": []}]}
            update = {"$push": {"videos.$.detection.face_recognition": from_dict(face_recognition)}}
            self.channel.update_one(query, update)
        except Exception as e:
            message = 'insert_face_recognition_in_video("' + channel_id + '","' +  video_id + '",' + face_recognition + ')'
            self.exception_message(e, message)

    def _filter_video_detected(self, video):
        try:
            detection = video['detection']
            face_recognition = detection['face_recognition']
            yolo = detection['yolo']
                
            count_yolo_positive = len(list(filter(lambda x: x['detected'] == True , yolo)))
            count_face_positive = len(list(filter(lambda x: x['detected'] == True , face_recognition)))
                
            if (count_face_positive > 0) or (count_yolo_positive > 0):
                self.video_id_download.append(video['video_id'])
        except Exception as e:
            message = '_filter_video_detected(' + video + ')'
            self.exception_message(e, message)

    def _filter_video_contains_caption(self, video):
        try:
            if video["caption_generated"] or video["caption_created"]:
                self.video_id_with_caption.append(video["video_id"])
        except Exception as e:
            message = '_filter_video_contains_caption(' + video + ')'
            self.exception_message(e, message)

    def get_videos_with_caption(self, channel_id):
        try:
            self.video_id_with_caption = []
            request = self.channel.find({"channel_id": channel_id})

            # extract the video IDs from the query results

            video_request = [iten["videos"] for iten in request]
            for item in video_request:
                videos = list(item)

            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                tasks = {executor.submit(self._filter_video_contains_caption, item): item for item in videos}
                for task in as_completed(tasks):
                    print(task)

            print(self.video_id_with_caption)
            return self.video_id_with_caption
        except Exception as e:
            message = 'get_videos_with_caption("' + channel_id + '")'
            self.exception_message(e, message)

    def get_videos_id_from_download(self, channel_id):
        try:
            self.video_id_download = []
            request = self.channel.find({"channel_id": channel_id})

            # extract the video IDs from the query results

            video_request = [iten["videos"] for iten in request]
            for item in video_request:
                videos = list(item)
                
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                tasks = {executor.submit(self._filter_video_detected, item): item for item in videos}
                for task in as_completed(tasks):
                    print(task)

            print(self.video_id_download)
            return self.video_id_download
        except Exception as e:
            message = 'get_videos_id_from_download("' + channel_id + '")'
            self.exception_message(e, message)

    def count_videos_channels(self):
        request = self.channel.find({})
        time = [channel['video_count'] for channel in request]
        soma = 0
        for item in time:
            soma += item
        print(soma)
        


    def count_channels_processed_time(self):
        channels = self.channel.find({})
        time = [channel['processing_time'] for channel in channels]
        soma = 0
        for item in time:
            soma += item
        print(soma/3600)

    def _statistic(self, video):
        try:
            self.channel_statistic.video_count += 1

            if (video['caption_generated'] == True or video['caption_created'] == True):
                self.channel_statistic.video_with_caption += 1

            detection = video['detection']
            face_recognition = detection['face_recognition']
            yolo = detection['yolo']
                
            yolo_positive = list(filter(lambda x: x['detected'] == True , yolo))
            face_positive = list(filter(lambda x: x['detected'] == True , face_recognition))

            count_left_yolo_positive = len(list(filter(lambda x: x['bottom_side'] == "bottom_left" , yolo_positive)))
            count_right_yolo_positive = len(list(filter(lambda x: x['bottom_side'] == "bottom_right" , yolo_positive)))
            count_left_face_positive = len(list(filter(lambda x: x['bottom_side'] == "bottom_left" , face_positive)))
            count_right_face_positive  =  len(list(filter(lambda x: x['bottom_side'] == "bottom_right" , face_positive)))

            if (count_left_yolo_positive > 0):
                self.channel_statistic.yolo_L += 1
            if (count_right_yolo_positive > 0):
                self.channel_statistic.yolo_R += 1
            if (count_left_face_positive > 0):
                self.channel_statistic.face_L += 1
            if (count_right_face_positive > 0):
                self.channel_statistic.face_R += 1
                

            if (count_left_yolo_positive > 0) or (count_left_face_positive > 0):
                self.channel_statistic.detected_left += 1
                self.channel_statistic.sum_time_video_L += video["duration"]

            if (count_right_yolo_positive > 0) or (count_right_face_positive > 0):
                self.channel_statistic.detected_right += 1
                self.channel_statistic.sum_time_video_R += video["duration"]

            if (len(yolo_positive) > 0 or len(face_positive) > 0):
                self.channel_statistic.video_detected_count += 1
                self.channel_statistic.sum_time_video_detected += video["duration"]
            
        except Exception as e:
            message = '_filter_video_detected(' + video + ')'
            self.exception_message(e, message)

    def get_channel_statistic(self, channel_id):
        try:
            self.channel_statistic = ChannelStatistic()
            request = self.channel.find({"channel_id": channel_id})

            video_request = [iten["videos"] for iten in request]
            for item in video_request:
                videos = list(item)
                
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                tasks = {executor.submit(self._statistic, item): item for item in videos}
                for task in as_completed(tasks):
                    print(task)

            return self.channel_statistic
        except Exception as e:
            message = 'get_videos_id_from_download("' + channel_id + '")'
            self.exception_message(e, message)


    def _get_all_videos_detected(self, video):
        try:
            detection = video['detection']
            face_recognition = detection['face_recognition']
            yolo = detection['yolo']
                
            yolo_positive = list(filter(lambda x: x['detected'] == True , yolo))
            face_positive = list(filter(lambda x: x['detected'] == True , face_recognition))

            # count_left_yolo_positive = len(list(filter(lambda x: x['bottom_side'] == "bottom_left" , yolo_positive)))
            count_right_yolo_positive = len(list(filter(lambda x: x['bottom_side'] == "bottom_right" , yolo_positive)))
            # count_left_face_positive = len(list(filter(lambda x: x['bottom_side'] == "bottom_left" , face_positive)))
            count_right_face_positive  =  len(list(filter(lambda x: x['bottom_side'] == "bottom_right" , face_positive)))

    
            if (count_right_yolo_positive >= MIN_YOLO_DETECTIONS) or (count_right_face_positive >= MIN_FR_DETECTIONS):
                self.videos_id_download.append(video['video_id'])

        except Exception as e:
            message = '_filter_video_detected(' + video + ')'
            self.exception_message(e, message)

    def get_all_videos_detected(self):
        try:
            self.videos_id_download = []
            channel_ids = self.get_channels_ids()
            for channel_id in channel_ids:
                self.channel_statistic = ChannelStatistic()
                request = self.channel.find({"channel_id": channel_id})

                video_request = [iten["videos"] for iten in request]
                for item in video_request:
                    videos = list(item)
                    
                with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                    tasks = {executor.submit(self._get_all_videos_detected, item): item for item in videos}
                    for task in as_completed(tasks):
                        print(task)

            return self.videos_id_download
        except Exception as e:
            message = 'get_videos_id_from_download("' + channel_id + '")'
            self.exception_message(e, message)



class ChannelStatistic():
    def __init__(self) -> None:
        self.video_count = 0
        self.video_detected_count = 0
        self.video_with_caption = 0
        self.yolo_L = 0
        self.yolo_R = 0
        self.face_L = 0
        self.face_R = 0
        self.detected_left = 0
        self.detected_right = 0
        self.sum_time_video_L = 0
        self.sum_time_video_R = 0
        self.sum_time_video_detected = 0

