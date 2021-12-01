import datetime
import os
from pathlib import Path
from tkinter import Tk, filedialog
from typing import List

from natsort import natsorted

from humanbytes import humanbytes

saved_path = Path("./last_path.txt")


def log(msg: str = ""):
    print(msg)


def clean_backup_folder(hips: List[Path]) -> int:
    hips = natsorted(hips)

    lists = []
    last_stem = ""

    for hip in list(hips):
        find = str(hip).rfind('_bak') + 4
        stem = str(hip)[:find]

        if stem != last_stem:
            lists.append([])

        lists[-1].append(hip)

        last_stem = stem

    root = str(hips[0].parent).split(r'\backup')[0]
    log()
    log(root)

    project_bytes_deleted = 0

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
                project_bytes_deleted += file_size
                # os.remove(hip)

        stem = str(Path(l[0]).stem).split("_bak")[0]
        ext = Path(l[0]).suffix
        log('{}\t>>>\tkept: {} ({} backups)\t---\tdeleted: {} ({} backups)'
            .format(stem+ext, humanbytes(kept_size), len(kept_hips), humanbytes(deleted_size), len(l)-len(kept_hips)))

    log(humanbytes(project_bytes_deleted))
    return project_bytes_deleted


def find_backup_folders(path: Path):
    total_deleted = 0
    for folder in path.rglob(''):
        if folder.stem == 'backup':
            # check if has "hip*" inside
            hips = list(folder.rglob('*.hip*'))
            if len(hips) > 3:  # min to keep
                total_deleted += clean_backup_folder(hips)

    log(f'\nTotal deleted: {humanbytes(total_deleted)}')


def ask_for_directory():
    path = open(saved_path).readline().rstrip() if saved_path.is_file() else ""

    root = Tk()
    root.withdraw()
    path = filedialog.askdirectory(initialdir=path)
    path = Path(path)

    if path.is_dir():
        with open(saved_path, "w") as f:
            f.write(str(path))
        find_backup_folders(path)


if __name__ == '__main__':
    ask_for_directory()
