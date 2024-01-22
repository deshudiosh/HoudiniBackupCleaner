import datetime
from operator import itemgetter
import os
from pathlib import Path
from pprint import pprint
from tkinter import Tk, filedialog, messagebox
from typing import List

from natsort import natsorted

from humanbytes import humanbytes

import color


saved_path = Path("./last_path.txt")
KEEP_EVERY_MINUTES = 15
ACTAULLY_REMOVE_FILES = False




def log(msg: str = "", bold=False):
    if not bold:
        print(msg)
    else:
        print(color.BOLD + msg + color.END)


def clean_backup_folder(hips: List[Path]) -> int:
    hips = natsorted(hips, key=lambda x: x.stem)

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
    deleted_hips = []

    for l in lists:
        kept_hips = []
        kept_size = 0
        deleted_size = 0
        last_time = None

        hip : Path
        for hip in reversed(l):
            keep = False
            mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(hip))
            file_size = os.stat(hip).st_size

            # always keep newest backup
            if not last_time:
                last_time = mod_time
                keep = True

            if last_time - mod_time >= datetime.timedelta(minutes=KEEP_EVERY_MINUTES):
                keep = True
                last_time = mod_time

            if keep:
                kept_hips.append(hip)
                kept_size += file_size
            else:
                deleted_size += file_size
                project_bytes_deleted += file_size
                
                deleted_hips.append({"file_name": hip.name, "file_path": str(hip.parent),"mod_time": mod_time.isoformat(), "file_size": file_size})

                if ACTAULLY_REMOVE_FILES:
                    os.remove(hip)
                    pass

        stem = str(Path(l[0]).stem).split("_bak")[0]
        ext = Path(l[0]).suffix
        log('{}\t>>>\tkept: {} ({} backups)\t---\tdeleted: {} ({} backups)'
            .format(stem+ext, humanbytes(kept_size), len(kept_hips), humanbytes(deleted_size), len(l)-len(kept_hips)))

    log(f'\nACTAULLY_REMOVE_FILES: {ACTAULLY_REMOVE_FILES}', bold=True)
    log(f'Deleted in folder: {humanbytes(project_bytes_deleted)}')
    log(f'Number of possibly deleted files: {len(deleted_hips)}')

    # store info about deleted hips
    # in case of fuckup while debbuging, dublicates possible - make sure to remove duplicates in other scripts while reading report
    if ACTAULLY_REMOVE_FILES:
        deleted_hips = natsorted(deleted_hips, key=itemgetter(*['file_name']))
        for hip_dict in deleted_hips:
            report_path = Path(hip_dict['file_path']) / "000_cleaned_backup_report.txt"
            hip_dict['del_time'] = datetime.datetime.now().isoformat()
            with open(report_path, 'a') as f:
                f.write(str(hip_dict)+"\n")            
    
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


def ask_for_directory(force = None):
    if not force:
        path = open(saved_path).readline().rstrip() if saved_path.is_file() else ""

        root = Tk()
        root.withdraw()
        path = filedialog.askdirectory(initialdir=path)
        path = Path(path)
    else:
        path = Path(force)

    if path.is_dir():
        if not force:
            with open(saved_path, "w") as f:
                f.write(str(path))

        find_backup_folders(path)


if __name__ == '__main__':
    print(f'{"-"*20}\n\nKeeping backup for every: {KEEP_EVERY_MINUTES}mins')
    ACTAULLY_REMOVE_FILES = True
    # ask_for_directory()
    # ask_for_directory(force = r'C:\Users\pgv\Desktop\hou bkp test\test part')
    ask_for_directory(force = r'D:\CURRENT PROJECTS\ModeMaison Labs')

