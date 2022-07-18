#!/usr/bin/env python3

import requests
import threading
import logging
from pathlib import Path
import re
import os
import sys
import math
import urllib
from queue import Queue
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
        self._url  = url
        self._header = self.header()
        self._filesize = self.filesize
        self._filename = self.filename
        self._resumable = self.supports_bytesrange()
        self._checksum_type, self._checksum = self.contains_checksum()

    def header(self):
        try:
            header = requests.head(self._url).headers
        except Exception as err:
            logging.critical("Error: {} occured during requesting the header information.".format(err))
            header = None
        finally:
            return header
    
    # for convenience we make filesize and filename property methods
    @property
    def filesize(self):
        if "Content-Length" in self._header.keys():
            filesize = int(self._header["Content-Length"])
        else:
            loggin.debug("No 'Content-Length' in header response.")
            filesize = None
        return filesize

    @property
    def filename(self):
        if "Content-Disposition" in self._header.keys():
            content_disposition = self._header["Content-Disposition"]
            filename = re.findall("filename=\"(.+)\"", d)[0]
            return filename
        else:
            logging.debug("No 'Content-Disposition' in header response.")
            basename = os.path.basename(self._url)
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
    def __init__(self, url, num_threads=4, **kwargs):
        super().__init__(url, **kwargs)
        self._num_threads = num_threads
        self.threads_bytes_range = self.threads_bytes_range()
    
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

    def threads_bytes_range(self):
        """Bytes range specific to a thread which will be downloaded by that thread."""
        thread_ranges = []
        range_start = 0
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



    def download(self):



if __name__ == "__main__":
    
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s', level=logging.DEBUG)

    # urlparser = UrlParser(url)
    # print(urlparser._filesize)
    # print(urlparser._filename)
    # print(urlparser._resumable)
    # print(urlparser._checksum_type, urlparser._checksum)

    xdl = Downloader(url)
    print(xdl.filesize)
    print(xdl.filename)
