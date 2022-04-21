from yt_dlp import YoutubeDL
import os
import webvtt
# import translators

DIR_NAME = 'Downloads/'  # В функциях не правильно используется это значение
id_video = 'dQYfflJ4V5Q'


def download_subtitles(video_id: str, path: str = '') -> str:
    """
    :param path:
    :param video_id: use youtube video ID;
    :return: name subtitles file if successfully downloaded;
    """
    vid_url = f'https://www.youtube.com/watch?v={video_id}'
    ydl_opts = {
        'outtmpl': f'/{path}{video_id}',
        'writesubtitles': True,
        'subtitle': '--write-sub --sub-lang en',
        'skip_download': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([vid_url])
    return path + get_true_subtitles_file_name(video_id, path)


def get_true_subtitles_file_name(video_id: str,  path: str = '') -> str:
    """
    Returns a string with the filename containing the passed ID value;
    :param path:
    :param video_id:
    :return:
    """
    file_names = list(filter(lambda file_name: video_id in file_name, os.listdir(path)))
    if not file_names:
        raise FileNotFoundError('No subtitles file for ID.')
    elif len(file_names) > 1:
        raise Exception(
            'Found multiple matches in filenames. Advise you to check the contents of the download folder.'
        )
    return file_names[0]


def get_all_words_from_subs_file(file_path: str) -> list:
    """
    :param file_path:
    :return:
    """
    subs = ' '.join([caption.text.lower() for caption in webvtt.read(file_path)])
    subs = ''.join([char for char in subs if char in "abcdefghijklmnopqrstuvwxyz ` "])
    return list(set(subs.split()))


def main():
    all_words = get_all_words_from_subs_file(download_subtitles(id_video, DIR_NAME))
    print(all_words)


if __name__ == '__main__':
    main()
