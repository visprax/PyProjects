#!/usr/bin/env python3

import requests
import logging
from pathlib import Path
import re
import os
import sys
import math
import urllib
import time
from queue import Queue
from threading import Thread
import shutil
# history
# progress bar
# download speed chart
# max speed, avg speed, total time
# proxy option
# testing
# TODO: add ftp support.

url="http://dls4.top-movies2filmha.tk/DonyayeSerial/series/The.Expanse/S01/480p/The.Expanse.S01E01.480p.x264.mkv"

"""
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
"""

class UrlParser:
    """Connect to the url server and retrieve header information."""
    def __init__(self, url):
        self.url  = url
        self._header = self.header()
        self.filesize = self.filesize()
        self.filename = self.filename()
        self.resumable = self.supports_bytesrange()
        self.checksum_type, self.checksum = self.contains_checksum()

    def header(self):
        try:
            header = requests.head(self.url).headers
        except Exception as err:
            logging.critical("Error: {} occured during requesting the header information.".format(err))
            header = None
        finally:
            return header
    
    def filesize(self):
        if "Content-Length" in self._header.keys():
            filesize = int(self._header["Content-Length"])
        else:
            loggin.debug("No 'Content-Length' in header response.")
            filesize = None
        return filesize
   
    def filename(self):
        if "Content-Disposition" in self._header.keys():
            content_disposition = self._header["Content-Disposition"]
            filename = re.findall("filename=\"(.+)\"", d)[0]
            return filename
        else:
            logging.debug("No 'Content-Disposition' in header response.")
            basename = os.path.basename(self.url)
            # filename in url could be url-encoded, so we decode it
            # if it's not decoded, this decoding will return the same basename
            filename = urllib.parse.unquote_plus(basename)
            return filename

    def supports_bytesrange(self):
        """Check if the server supports byte range. This determines resume capability."""
        if not "Accept-Ranges" in self._header.keys():
            loggin.debug("bytes range is not supported.")
            return False
        elif self._header["Accept-Ranges"] == "none":
            loggin.debug("Bytes range is not supported.")
            return False
        else:
            return True
    
    def contains_checksum(self):
        if "Content-MD5" in self._header.keys():
            checksum_type="MD5"
            checksum = self._header["Content-MD5"]
            return checksum_type, checksum
        elif "x-goog-hash" in self._header.keys():
            goog_hash = self._header["x-goog-hash"]
            if goog_hash.startswith("crc32c") and "md5" not in goog_hash:
                checksum_type="CRC32C"
                checksum = re.compile("crc32c=(.*)").findall(goog_hash)
            elif goog_hash.startswith("md5") and "crc32c" not in goog_hash:
                checksum_type = "MD5"
                checksum = re.compile("md5=(.*)").findall(goog_hash)
            else:
                checksum_type="CRC32C,MD5"
                checksum_strings = goog_hash.split(',')
                checksum = []
                for checksum_string in checksum_strings:
                    if checksum_string.startswith("crc32c"):
                        checksum1 = re.compile("crc32c=(.*)").findall(checksum_string)
                        checksum.append(checksum1)
                    else:
                        checksum2 = re.compile("md5=(.*)").findall(checksum_string)
                        checksum.append(checksum2)
        else:
            checksum_type = None
            checksum = None

        return checksum_type, checksum


class Downloader(UrlParser):
    def __init__(self, url, num_threads=4, dldir=".", **kwargs):
        super().__init__(url, **kwargs)
        self._num_threads = num_threads
        self._dldir = dldir
        self.filepath = os.path.join(dldir, self.filename)
        # [(0, 9), (10, 19), (20, 28)]
        self._byte_ranges = self.get_byte_ranges()
        # Queue({"chunk_id": 0, "chunk_range": (0, 10), "interrupted": False}, ...)
        self.dlqueue = self.get_dlqueue()
        self.start_time = None
        # filename pattern used for file chunks
        self._chunk_filename = self.filename + ".part"
    
    @property
    def num_threads(self):
        return self._num_threads

    @num_threads.setter
    def num_threads(self, num_threads):
        if num_threads <= 0:
            raise ValueError("Number of threads should be a positive integer.")
        if not isinstance(num_threads, int):
            raise TypeError("Number of threads should be of type integer.")
        self._num_threads = num_threads
    
    @num_threads.deleter
    def num_threads(self):
        raise AttributeError("num_threads can't be deleted. Set to 1 to use only one thread.")
    
    @property
    def dldir(self):
        return self._dldir
    
    @dldir.setter
    def dldir(self, dldir):
        disk_total_size, disk_used_size, disk_available_size = shutil.disk_usage(dldir)
        if disk_available_size < self.filesize:
            raise ValueError("Provided download directory doesn't have enough storage space.")
        elif not os.path.isdir(dldir):
            raise FileNotFoundError("The download directory doesn't exists.")
        else:
            self._dldir = dldir

    def get_byte_ranges(self):
        """Bytes range specific to a thread which will be downloaded by that thread."""
        thread_ranges = []
        chunk_start = 0
        chunk_size = math.ceil(self.filesize / self.num_threads)
        if chunk_size == 1:
            logging.warning("Filesize {}, too short for {} threads. Using 1 thread.".format(self.filesize, self.num_threads))
            self.num_threads = 1

        for _ in range(self.num_threads):
            if (chunk_start + chunk_size) < self.filesize:
                bytes_range = (chunk_start, chunk_start+chunk_size-1)
            else:
                bytes_range = (chunk_start, self.filesize)
            chunk_start += chunk_size
            thread_ranges.append(bytes_range)

        return thread_ranges

    def get_dlqueue(self):
        """Queue the chunks for threads to pick from."""
        # {"0": {"range": (0, 10), "interrupted": False}, }
        dlqueue = Queue(maxsize=0)
        for chunk_id, chunk_range in enumerate(self._byte_ranges):
            item = {"chunk_id": chunk_id, "chunk_range": chunk_range, "interrupted": False}
            dlqueue.put(item)
        return dlqueue

    def timestamp(self):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        return now

    def download(self):
        """Main driver function for starting downloader threads."""
        self.start_time = self.timestamp()
        if self.resumable:
            logging.debug("Starting download in a resumable mode.")
            for _ in range(self.num_threads):
                thread = Thread(target=self.download_chunk)
                thread.daemon = True
                thread.start()
            logging.debug("Download threads have been started.")
       
        self.log_dlstat()
        # wait until all threads are done
        self.dlqueue.join()

        logging.debug("Merging file chunks into single file.")

    
    def log_dlstat(self):
        while not self.isfinished():
            dlstat = self.dlstat()
            stat_str = ""
            for stat in dlstat:
                stat_str += "Part {}: {}%\t".format(*stat)
            logging.info("Download status: {}".format(stat_str))
            time.sleep(5)
        if self.isfinished():
            logging.info("Download complete.")

    def dlstat(self):
        """Get download percentage for each thread."""
        # [(1, 98), (2, 65), ...]
        dlstat = []
        for thread_idx in range(self.num_threads):
            chunk_path = os.path.join(self.dldir, self._chunk_filename+str(thread_idx))
            if os.path.isfile(chunk_path):
                chunk_dlsize = os.stat(chunk_path).st_size
                chunk_dlperc = round((chunk_dlsize / (self.filesize/self.num_threads)) * 100, 2)
                dlstat.append((thread_idx, chunk_dlperc))
            else:
                dlstat.append((thread_idx, 0.00))
        return dlstat

    def isfinished(self):
        dlstat = dlstat()
        sec_elm = lambda x: x[1]
        percentages = [sec_elm(stat) for stat in dlstat]
        if all(percent == 100.00 for percent in percentages):
            return True
        else:
            return False








if __name__ == "__main__":
    
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s', level=logging.DEBUG)

    # urlparser = UrlParser(url)
    # print(urlparser.filesize)
    # print(urlparser.filename)
    # print(urlparser.resumable)
    # print(urlparser.checksum_type, urlparser.checksum)

    xdl = Downloader(url)
    print(xdl.filesize)
    print(xdl.filename)
    xdl.download()
    print(xdl.start_time)

