from channel_id_extractor import extract_chanel_ids
from channel import Channel
from videos_download_persistence import VideosResultsDB
from partial_downloader import PartialDownloader
from subtitle_downloader import SubtitleDownloader
from video_downloader import VideoDownloader
from face_detection import FaceDetection
from video_id_generator import get_video_ids
from image_cropping import CroppingGenerator
from txt_reader import read_archive_with_link_channels
from shutil import make_archive
from constants import *
import time
import os
import shutil

#O arquivo de entrada e os paramêtros do Script são ajustados nas constantes. 

if __name__ == '__main__':
    subtitle_downloader = SubtitleDownloader(['pt-BR', 'pt'], SUBTITLES_PATH)

    channels_url_list = read_archive_with_link_channels(INPUT_URL_TXT)

    channel_ids = extract_chanel_ids(channels_url_list)
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
        cropping_generator.generate_bottom_corner_croppings(BOTTOM_RIGHT, 0.55, 0.3) # porcentagem da altura e da largura da imagem para definir o tamanho dos recortes
        cropping_generator.generate_bottom_corner_croppings(BOTTOM_LEFT, 0.55, 0.3) # canto inferior esquerdo

        face_detection = FaceDetection(channel_id, f"{CROPPED_IMGS_PATH}/{BOTTOM_RIGHT}") # primeiro, processa os recortes dos cantos inferiores direitos
        processed_imgs_path = f"{PROCESSED_IMAGES_PATH}/{BOTTOM_RIGHT}"
        face_detection.detect(BOTTOM_RIGHT, processed_imgs_path)
        
        #face_detection.set_images_directory(f"{PROCESSED_IMAGES_PATH}/{BOTTOM_RIGHT}/{FACE_RECOGNITION_DIR}/{FACES_NEGATIVE_DIR}") 
        face_detection.detect_yolo(BOTTOM_RIGHT, processed_imgs_path)

        face_detection.set_images_directory(f"{CROPPED_IMGS_PATH}/{BOTTOM_LEFT}") # agora, processa os do lado esquerdo
        processed_imgs_path = f"{PROCESSED_IMAGES_PATH}/{BOTTOM_LEFT}"
        face_detection.detect(BOTTOM_LEFT, processed_imgs_path)
        
        # face_detection.set_images_directory(f"{PROCESSED_IMAGES_PATH}/{BOTTOM_LEFT}/{FACE_RECOGNITION_DIR}/{FACES_NEGATIVE_DIR}")
        face_detection.detect_yolo(BOTTOM_LEFT, processed_imgs_path)

        time_end = time.time()
        Channel(channel_id).set_processing_time(time_end - time_init)
        
        #Compactado arquivo para verificar as detecções feitas
        if os.path.isdir(PROCESSED_IMAGES_PATH):
            shutil.make_archive(PROCESSED_IMAGES_ZIP_PATH + '/processed_' + channel_id, 'zip', PROCESSED_IMAGES_PATH)
        
        for files in os.listdir(BASE_PATH):
            path = os.path.join(BASE_PATH, files)
            try:
                shutil.rmtree(path)
            except OSError:
                os.remove(path)

        videos_download = Channel(channel_id).get_videos_id_from_download()
        VideosResultsDB().persist_videos_afirmative(videos_download)


    vid_ids_to_download = VideosResultsDB().get_videos_from_download()
    videos_to_download = []
    for video in vid_ids_to_download:
        if (not os.path.isfile(VIDEOS_PATH + '/' + video + '.mp4')):
            videos_to_download.append(video)

    video_downloader = VideoDownloader(VIDEOS_PATH)
    video_downloader.download(videos_to_download)

    subtitle_downloader.download(vid_ids_to_download)
