#!/usr/bin/env python3

import requests
import threading
import logging
from pathlib import Path

url="http://dls4.top-movies2filmha.tk/DonyayeSerial/series/The.Expanse/S01/480p/The.Expanse.S01E01.480p.x264.mkv"

def download_file(url, resume_byte_pos):
    local_filename = url.split('/')[-1]
    # NOTE the stream=True parameter below
    
    resume_header = ({'Range': f'bytes={resume_byte_pos}-'} if resume_byte_pos else None)
    initial_pos = resume_byte_pos if resume_byte_pos else 0

    print("Active threads: {}".format(threading.active_count()))

    with requests.get(url, stream=True, verify=False, allow_redirects=True, headers=resume_header) as r:
        r.raise_for_status()
        if "Content-Disposition" in r.headers.keys():
            filename = r.headers["Content-Disposition"]
        if "Content-Length" in r.headers.keys():
            filesize = int(r.headers["Content-Length"])

        with open(local_filename, 'ab') as f:
            chunk_size=8192
            for chunk in r.iter_content(chunk_size=chunk_size): 
                # If you have chunk encoded response uncomment if
                # and set chunk_size parameter to None.
                #if chunk: 
                f.write(chunk)
            # shutil.copyfileobj(r.raw, f, length=chunk_size)
    return local_filename





def create_download_threads(url, resume_byte_pos):
    download_thread = threading.Thread(target=download_file, args=(url, resume_byte_pos))
    download_thread.start()


download_dir = Path(".")
file = download_dir / url.split('/')[-1]
file_size_offline = file.stat().st_size
r = requests.head(url)
file_size_online = int(r.headers.get('content-length', 0))

for i in range(0, 4):
    create_download_threads(url, file_size_offline)
