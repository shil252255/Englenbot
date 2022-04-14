from yt_dlp import YoutubeDL
import os
import webvtt
from collections import Counter
import translators
from psql_moduls import psql_command

DIR_NAME = 'Downloads/'
id_video = 'dQYfflJ4V5Q'
ydl_opts = {'outtmpl': f'/{DIR_NAME}%(title)s_{id_video}.mp4',
            'format': '(bestvideo[width>=1080][ext=mp4]/bestvideo)+bestaudio/best',
            'writesubtitles': True,
            'subtitle': '--write-sub --sub-lang en'}


def download_file():
    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([f'https://www.youtube.com/watch?v={id_video}'])


file_names = os.listdir(DIR_NAME)
file_name = [file_name for file_name in file_names if id_video in file_name and '.vtt' in file_name][0]

all_sub = ''
for subtitles in webvtt.read(f'{DIR_NAME}{file_name}'):
    all_sub += ' ' + subtitles.text.lower()
all_sub = ''.join([char for char in all_sub if char in "abcdefghijklmnopqrstuvwxyz '"])

all_words = all_sub.split()

all_uniq_words = [word[0] for word in Counter(all_words).most_common()]
translate_words = translators.google('\n'.join(all_uniq_words).split('\n'))

print(len(all_uniq_words))
print(len(translate_words))

for word, num in enumerate(all_uniq_words):
    psql_command(f"INSERT INTO eng_words(word, short_rus_translation)"
                 f"VALUES("
                 f"'{word}',"
                 f"'{translate_words[num]}');")


if __name__ == '__main__':
    pass