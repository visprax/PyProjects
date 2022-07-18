#!/usr/bin/env python3

import requests
import threading
import logging
from pathlib import Path
import re
import urllib

# history
# progress bar
# download speed chart
# max speed, avg speed, total time
# proxy option
# TODO: add ftp support.

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

class UrlParser():
    """Connect to the url server and retrieve header information."""
    def __init__(self, url):
        self._url  = url
        self._header = self.header()
        self._filesize = self.filesize()
        self._filename = self.filename()
        self._resumable = self.supports_bytesrange()

    def header(self):
        return requests.head(self._url)
    
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
            basename = self._url.split('/')[-1]
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
                checksums = []
                for checksum_string in checksum_strings:
                    if checksum_string.startswith("crc32c"):
                        checksum = re.compile("crc32c=(.*)").findall(checksum_string)
                        checksums.append(checksum)
                    else:
                        checksum = re.compile("md5=(.*)").findall(checksum_string)
                        checksums.append(checksum)




class Downloader():
