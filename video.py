from recognition import RecognitionInterpreter
class Video:
    def __init__(self, video_id):
        self.video_id = video_id
        self.caption_generated = False
        self.caption_created = False
        self.duration = 0
        self.recognition = RecognitionInterpreter()

    def set_caption_generated(self, caption_generated):
        self.caption_generated = caption_generated

    def set_caption_created(self, caption_created):
        self.caption_created = caption_created

    def set_duration(self, duration):
        self.duration = duration

    def add_recognition_results(self, recognition):
        self.recognition = recognition
        