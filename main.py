import os
import datetime
from pathlib import Path
from pprint import pprint
from tkinter import Tk, filedialog

from natsort import natsorted
import wx
from wx import EmptyString

from humanbytes import humanbytes

saved_path = Path("./last_path.txt")


def log(msg: str):
    print(msg)


def clean_backup_folder(path: Path):
    files = [str(x) for x in path.glob('**/*.hip*')]
    files = natsorted(files)

    lists = []
    last_stem = ""

    for file in list(files):
        find = str(file).rfind('_bak') + 4
        stem = str(file)[:find]

        if stem != last_stem:
            lists.append([])

        lists[-1].append(file)

        last_stem = stem

    root = str(path.parent).split(r'\backup')[0]
    log(str(path.parent).split(r'\backup')[0])

    total_deleted = 0

    for l in lists:
        kept_hips = []
        kept_size = 0
        deleted_size = 0
        last_time = None
        for hip in reversed(l):
            keep = False
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(hip))
            file_size = os.stat(hip).st_size

            # always keep newest backup
            if not last_time:
                last_time = mod_time
                keep = True

            if last_time - mod_time >= datetime.timedelta(minutes=15):
                keep = True
                last_time = mod_time

            if keep:
                kept_hips.append(hip)
                kept_size += file_size
            else:
                deleted_size += file_size
                total_deleted += file_size
                # os.remove(hip)

        hip_stem = str(Path(l[0]).stem).split("_bak")[0]
        log('{} >>> kept: {} ({} backups) --- deleted: {} ({} backups)'
            .format(hip_stem, humanbytes(kept_size), len(kept_hips), humanbytes(deleted_size), len(l)-len(kept_hips)))

    log(humanbytes(total_deleted))


def find_backup_subdirs(path):
    path = Path(path)
    for dir in path.rglob(''):
        if dir.stem == 'backup':
            # check if has "hip*" inside
            hips = dir.rglob('*.hip*')
            print(dir, len(list(hips)))


def ask_for_directory():
    path = open(saved_path).readline().rstrip() if saved_path.is_file() else ""

    root = Tk()
    root.withdraw()
    path = filedialog.askdirectory(initialdir=path)

    if path:
        with open(saved_path, "w") as f:
            f.write(path)
        find_backup_subdirs(path)


if __name__ == '__main__':
    ask_for_directory()
