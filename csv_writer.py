from constants import VIDEO_IDS_FILENAME, PROCESSED_IMAGES_FILENAME, PROCESSED_IMAGES_YOLO_FILENAME, SUBTITLES_FILENAME
import csv

def write_csv(filename, info_list):
    with open(filename, 'a', newline='', encoding='utf-8') as file:
        w = csv.writer(file)
        w.writerows(info_list)


def write_transcriptions_info(transcript_list):
    write_csv(SUBTITLES_FILENAME, transcript_list)


def write_recognized_faces(info_list):
    write_csv(PROCESSED_IMAGES_FILENAME, info_list)


def write_recognized_faces_yolo(info_list):
    write_csv(PROCESSED_IMAGES_YOLO_FILENAME, info_list)


def write_video_ids(video_url_list):
    with open(VIDEO_IDS_FILENAME, 'a', encoding='utf-8') as f:
        for url in video_url_list:
            id = url.replace("https://www.youtube.com/watch?v=", '')
            f.write(id + '\n')
