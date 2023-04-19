from constants import ARCHIVE_TXT_URL_FILES_DIR

def read_archive_with_link_channels(archive_name):
    archive = open(ARCHIVE_TXT_URL_FILES_DIR + archive_name + ".txt")
    request = archive.readlines()
    lines = []
    for line in request:
        lines.append(line.replace('\n',''))
    return lines
