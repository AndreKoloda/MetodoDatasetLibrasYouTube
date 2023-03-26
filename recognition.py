class FaceRecognition:
    def __init__(self, bottom_side, index, recognized = False) -> None:
        self.bottom_side = bottom_side
        self.index = index
        self.recognized = recognized

class Yolo:
    def __init__(self, bottom_side, index, recognized = False) -> None:
        self.bottom_side = bottom_side
        self.index = index
        self.recognized = recognized

class RecognitionInterpreter:
    def __init__(self) -> None:
        self.face_recognition = []
        self.yolo = []

    def add_face_recognition(self, index, recognized):
        recognition_face =  FaceRecognition(index= index, recognized= recognized)
        self.face_recognition.append(recognition_face)

    def add_yolo_recognition(self, index, recognized):
        recognition_yolo =  Yolo(index= index, recognized= recognized)
        self.yolo.append(recognition_yolo)