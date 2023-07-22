# Скрипт сортування файлів у заданій папці
# Аргумент скрипта - ім'я папки

import re
import sys
from pathlib import Path
import shutil

CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")
TRANS = {}
for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()

def normalize(name: str) -> str: # Нормалізація імені файла
    t_name = name.translate(TRANS)
    t_name = re.sub(r'[^a-zA-Z0-9_.]', '_', t_name)
    return t_name

JPEG_IMAGES = []
JPG_IMAGES = []
PNG_IMAGES = []
SVG_IMAGES = []
MP3_AUDIO = []
AVI_VIDEO = []
MPEG_VIDEO = []
MP4_VIDEO = []
DOC_WORD = []
DOC_TXT = []
MY_OTHER = []
ARCHIVES = []

REGISTER_EXTENSION = {
    'JPEG': JPEG_IMAGES,
    'JPG': JPG_IMAGES,
    'PNG': PNG_IMAGES,
    'SVG': SVG_IMAGES,
    'MP3': MP3_AUDIO,
    'AVI': AVI_VIDEO,
    'MPEG': MPEG_VIDEO,
    'MP4': MP4_VIDEO,
    'DOCX': DOC_WORD,
    'DOC': DOC_WORD,
    'TXT': DOC_TXT,
    'ZIP': ARCHIVES
}

FOLDERS = []
EXTENSION = set()
UNKNOWN = set()

def get_extension(filename: str) -> str:
    return Path(filename).suffix[1:].upper()  # перетворюємо розширення файлу на назву папки jpg -> JPG

def scan(folder: Path) -> None:
    for item in folder.iterdir():
        # Якщо це папка то додаємо її до списку FOLDERS і переходимо до наступного елемента папки
        if item.is_dir():
            # перевіряємо, щоб папка не була тією в яку ми складаємо вже файли
            if item.name not in ('archives', 'video', 'audio', 'documents', 'images', 'MY_OTHER'):
                FOLDERS.append(item)
                # скануємо вкладену папку
                scan(item)  # рекурсія
            continue  # переходимо до наступного елементу в сканованій папці

        #  Робота з файлом
        ext = get_extension(item.name)  # беремо розширення файлу
        fullname = folder / item.name  # беремо шлях до файлу
        if not ext:  # якщо файл немає розширення то додаєм до невідомих
            MY_OTHER.append(fullname)
        else:
            try:
                container = REGISTER_EXTENSION[ext]
                EXTENSION.add(ext)
                container.append(fullname)
            except KeyError:
                # Якщо ми не зареєстрували розширення у REGISTER_EXTENSION, то додаємо до невідомих
                UNKNOWN.add(ext)
                MY_OTHER.append(fullname)

def handle_file(filename: Path, target_folder: Path) -> None:
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / normalize(filename.name))

def handle_other(filename: Path, target_folder: Path) -> None:
    target_folder.mkdir(exist_ok=True, parents=True)
    filename.replace(target_folder / normalize(filename.name))

def handle_archive(filename: Path, target_folder: Path) -> None:
    target_folder.mkdir(exist_ok=True, parents=True)  # робимо папку для архіва
    folder_for_file = target_folder / normalize(filename.name.replace(filename.suffix, ''))
    folder_for_file.mkdir(exist_ok=True, parents=True)
    try:
        shutil.unpack_archive(filename, folder_for_file)
    except shutil.ReadError:
        print('It is not archive')
        folder_for_file.rmdir()
    filename.unlink()

def handle_folder(folder: Path):
    try:
        folder.rmdir()
    except OSError:
        print(f"Can't delete folder: {folder}")

def main(folder: Path):
    scan(folder)
    for file in JPEG_IMAGES:
        handle_file(file, folder / 'images' / 'JPEG')
    for file in JPG_IMAGES:
        handle_file(file, folder / 'images' / 'JPG')
    for file in PNG_IMAGES:
        handle_file(file, folder / 'images' / 'PNG')
    for file in SVG_IMAGES:
        handle_file(file, folder / 'images' / 'SVG')
    for file in MP3_AUDIO:
        handle_file(file, folder / 'audio' / 'MP3')
    for file in AVI_VIDEO:
        handle_file(file, folder / 'video' / 'AVI')
    for file in MPEG_VIDEO:
        handle_file(file, folder / 'video' / 'MPEG')
    for file in MP4_VIDEO:
        handle_file(file, folder / 'video' / 'MP4')
    for file in DOC_WORD:
        handle_file(file, folder / 'documents' / 'DOC')
    for file in DOC_TXT:
        handle_file(file, folder / 'documents' / 'TXT')

    for file in MY_OTHER:
        handle_other(file, folder / 'MY_OTHER')
    for file in ARCHIVES:
        handle_archive(file, folder / 'archives')

def start():
    try:
        if sys.argv[1]:
            folder_for_scan = Path(sys.argv[1])
            print(f'Start in folder {folder_for_scan.resolve()}')
            main(folder_for_scan.resolve())
        for folder in FOLDERS[::-1]:
            handle_folder(folder)
    except IndexError:
        print("Введіть ім'я папки")

