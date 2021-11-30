import os
import datetime
from pathlib import Path
from pprint import pprint

from natsort import natsorted
from humanbytes import humanbytes


def main():
    path = Path(r'C:\Users\pgv\Desktop\backup')

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

            # print(hip, mod_time, 'keep' if keep else '')

        print('kept: {} ({} backups) --- deleted: {} ({} backups)'
              .format(humanbytes(kept_size), len(kept_hips), humanbytes(deleted_size), len(l)-len(kept_hips)))

    print(humanbytes(total_deleted))


if __name__ == '__main__':
    main()
