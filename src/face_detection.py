import os
import face_recognition as fr
import glob
from yolo import YoloFace
from channel import Channel
from detection import Yolo as YoloObj, FaceRecognition as FaceObj
from image_cropping import Image
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path 
from tqdm import tqdm
from threading import Semaphore
from constants import MAX_WORKERS, ID_FRAME_SEPARATOR, FACE_RECOGNITION_DIR, YOLO_DIR, FACES_NEGATIVE_DIR, FACES_POSITIVE_DIR, ID, FRAME


class FaceDetection:
    def __init__(self, channel_id, images_directory='images'):
        self.channel_id = channel_id
        self.images_directory = images_directory
        self._semaphore = Semaphore()
        self._yoloface = None

    def set_images_directory(self, images_directory):
        self.images_directory = images_directory

    def get_face_locations(self, img_path):
        img = fr.load_image_file(img_path)
        self._semaphore.acquire() 
        try:
            face_locations = fr.face_locations(img)
            return face_locations
        finally:
            self._semaphore.release()
    
    def has_faces(self, img_path):
        return bool(self.get_face_locations(img_path)) 
    
    def detect(self, bottom_side, processed_images_directory=''):
        print(f"\nDetecting faces... ({self.images_directory})")

        files = glob.glob(self.images_directory + '/*')
        pbar = tqdm(total=len(files))
      
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = {executor.submit(self._detect, img_path, bottom_side, processed_images_directory): img_path for img_path in files}
            for task in as_completed(tasks):
                pbar.update()
        
        pbar.close()
        print("Face detection completed.\n")

    def _detect(self, image_path, bottom_side, processed_images_directory=''):
        has_faces = self.has_faces(image_path)
        self._set_detection_output(image_path, bottom_side, has_faces, processed_images_directory)
            
    def detect_yolo(self, bottom_side, processed_images_directory=''):
        print(f"\nDetecting faces using YOLO... ({self.images_directory})")

        if not self._yoloface:
            self._yoloface = YoloFace()
        
        files = glob.glob(self.images_directory + '/*')

        for img_path in tqdm(files):
            self._detect_yolo(img_path, bottom_side, processed_images_directory)
        
        print("YOLO detection completed.\n")
    
    def _detect_yolo(self, img_path, bottom_side, processed_images_directory=''):
        has_faces = self._yoloface.detect(img_path)
        self._set_detection_output(img_path, bottom_side, has_faces, processed_images_directory, yolo=True)

    def _set_detection_output(self, img_path, bottom_side, target_found, processed_images_directory, yolo=False):
        if processed_images_directory != '':
            if yolo:
                output_path = Path(processed_images_directory).joinpath(YOLO_DIR)
            else:
                output_path = Path(processed_images_directory).joinpath(FACE_RECOGNITION_DIR) 

            if target_found:
                output_path = output_path.joinpath(FACES_POSITIVE_DIR)
            else:
                output_path = output_path.joinpath(FACES_NEGATIVE_DIR)
            
            Image(img_path).save(str(output_path))

        self._update_video_db(yolo, bottom_side, os.path.basename(img_path), target_found)
    
    def _update_video_db(self, yolo, bottom_side, filename, detected):
        split_filename = Path(filename).stem.split(ID_FRAME_SEPARATOR)

        if len(split_filename) > 1:
            frame = split_filename[FRAME]
        else:
            frame = '0'

        if yolo:
            yolo_obj = YoloObj(bottom_side, frame, detected)
            Channel(self.channel_id).insert_yolo_detection_in_video(split_filename[ID], yolo_obj)
        else:
            face_obj = FaceObj(bottom_side, frame, detected)
            Channel(self.channel_id).insert_face_recognition_in_video(split_filename[ID], face_obj)

if __name__ == '__main__':
    pass

