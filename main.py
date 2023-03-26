from channel_id_extractor import extract_chanel_ids
from channel import Channel
from videos_download_persistence import VideosResultsDB
from partial_downloader import PartialDownloader
from subtitle_downloader import SubtitleDownloader
from video_downloader import VideoDownloader
from facial_recognition import FaceRecognition
from video_id_generator import get_video_ids
from image_cropping import CroppingGenerator
from shutil import make_archive
from constants import *
import csv
import time
import os
import shutil
# from id_generator import get_ids_from_channel, sort_ids_obtained_from_channel, get_video_ids_from_playlist

if __name__ == '__main__':
    subtitle_downloader = SubtitleDownloader(['pt-BR', 'pt'], SUBTITLES_PATH)

    channel_ids = extract_chanel_ids(CHANNEL_URL_LIST)
    get_video_ids()
    channel_ids = Channel().get_channels_not_processed_ids()

    for channel_id in channel_ids:
        time_init = time.time()
    
        vid_ids_with_transcripts = subtitle_downloader.filter_only_having_transcripts(channel_id)
    
        partial_downloader = PartialDownloader(vid_ids_with_transcripts, PARTIAL_DOWNLOADS_PATH, FRAMES_PATH)
        partial_downloader.set_video_time_info(channel_id)

        partial_downloader.download() # captura de fragmento do video
   
        partial_downloader.get_frames() # captura de frame do fragmento de video

        cropping_generator = CroppingGenerator(FRAMES_PATH, CROPPED_IMGS_PATH) # caminho de entrada e de saída dos recortes
        cropping_generator.generate_bottom_corners_croppings(0.55, 0.3) # porcentagem da altura e da largura da imagem para definir o tamanho dos recortes

        face_recognition = FaceRecognition(channel_id, f"{CROPPED_IMGS_PATH}/{BOTTOM_RIGHT}") # primeiro, processa os recortes dos cantos inferiores direitos
        processed_imgs_path = f"{PROCESSED_IMAGES_PATH}/{BOTTOM_RIGHT}"
        face_recognition.recognize(BOTTOM_RIGHT, processed_imgs_path)
        
        #face_recognition.set_images_directory(f"{PROCESSED_IMAGES_PATH}/{BOTTOM_RIGHT}/{FACE_RECOGNITION_DIR}/{FACES_NEGATIVE_DIR}") 
        face_recognition.recognize_yolo(BOTTOM_RIGHT, processed_imgs_path)

        face_recognition.set_images_directory(f"{CROPPED_IMGS_PATH}/{BOTTOM_LEFT}") # agora, processa os do lado esquerdo
        processed_imgs_path = f"{PROCESSED_IMAGES_PATH}/{BOTTOM_LEFT}"
        face_recognition.recognize(BOTTOM_LEFT, processed_imgs_path)
        
        # face_recognition.set_images_directory(f"{PROCESSED_IMAGES_PATH}/{BOTTOM_LEFT}/{FACE_RECOGNITION_DIR}/{FACES_NEGATIVE_DIR}")
        face_recognition.recognize_yolo(BOTTOM_LEFT, processed_imgs_path)

        time_end = time.time()
        Channel(channel_id).set_processing_time(time_end - time_init)
        
        if os.path.isdir(PROCESSED_IMAGES_PATH):
            make_archive(PROCESSED_IMAGES_ZIP_PATH + '/processed_' + channel_id, 'zip', PROCESSED_IMAGES_PATH)
        
        for files in os.listdir(BASE_PATH):
            path = os.path.join(BASE_PATH, files)
            try:
                shutil.rmtree(path)
            except OSError:
                os.remove(path)

        videos_download = Channel(channel_id).get_videos_id_from_download()
        VideosResultsDB().persist_videos_afirmative(videos_download)


    vid_ids_to_download = VideosResultsDB().get_videos_from_download()
    video_downloader = VideoDownloader(VIDEOS_PATH)
    video_downloader.download(vid_ids_to_download[4500:5500])

    subtitle_downloader.download(vid_ids_to_download[4500:5500])
