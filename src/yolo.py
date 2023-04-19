from yoloface import face_analysis
from constants import CONF_YOLO

class YoloFace:
    def __init__(self):
        self.face = face_analysis() #  Auto Download a large weight files from Google Drive.
                                    #  only first time.
                                    #  Automatically  create folder .yoloface on cwd.

    def detect(self, img_path):
        img,box,conf = self.face.face_detection(image_path=img_path,model='tiny')
        return (len(box) > 0) and (conf[0] > CONF_YOLO)


if __name__ == '__main__':
    pass
