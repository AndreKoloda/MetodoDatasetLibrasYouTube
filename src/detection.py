class FaceRecognition:
    def __init__(self, bottom_side, index, detected = False) -> None:
        self.bottom_side = bottom_side
        self.index = index
        self.detected = detected

class Yolo:
    def __init__(self, bottom_side, index, detected = False) -> None:
        self.bottom_side = bottom_side
        self.index = index
        self.detected = detected

class DetectionInterpreter:
    def __init__(self) -> None:
        self.face_recognition = []
        self.yolo = []

    def add_face_recognition(self, index, recognized):
        detection_face =  FaceRecognition(index= index, recognized= recognized)
        self.face_recognition.append(detection_face)

    def add_yolo_recognition(self, index, recognized):
        detection_yolo =  Yolo(index= index, recognized= recognized)
        self.yolo.append(detection_yolo)
