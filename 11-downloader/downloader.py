#!/usr/bin/env python3

"""Multithreaded downloader with progress bar and live download speed chart."""

import re
import os
import sys
import math
import time
import zlib
import shutil
import urllib
import hashlib
import logging
import argparse
import requests
import threading
from queue import Queue
from rich.progress import (
        BarColumn,
        DownloadColumn,
        Progress,
        TaskID,
        TextColumn,
        TimeRemainingColumn,
        TransferSpeedColumn,
        )

# TODO:
# history
# progress bar
# download speed chart
# max speed, avg speed, total time
# proxy option
# testing
# add ftp support. youtube through yt-dlp, torrent
# pass args object to classes

url="https://mirror.wayne.edu/ubuntu/releases/22.04/ubuntu-22.04-desktop-amd64.iso"
# url = "https://s3003.upera.tv/2775411-0-GangsofLondonSE-480.mp4?owner=6056023&ref=30144&id=2775411655134678&md5=Md70N_Jm0c_LYwilh_gmMg&expires=1658381992c"

class UrlParser:
    """Connect to the url server and retrieve header information."""
    def __init__(self, args):
        self.args = args
        self.url  = url # args.url
        self._header = self.header()
        self.filesize = self.filesize()
        self.filename = self.filename()
        self.resumable = self.supports_bytesrange()
        self.checksum_type, self.checksum = self.contains_checksum()

    def header(self):
        try:
            header = requests.head(self.url, allow_redirects=True, verify=self.args.check_certificate).headers
            return header
        except Exception as err:
            logging.critical("Error occured during requesting the header information: {}".format(err))
            header = None
            raise SystemExit("Error, couldn't connect to server: {}".format(err))
    
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
            logging.debug("bytes range is not supported.")
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
        # start and end time stamp of download
        self.start_time = None
        self.end_time = None
        # filename pattern used for file chunks
        self._chunk_filename = self.filename + ".part"
        # defualt write mode, could be 'wb' or 'ab'
        self._write_mode = "wb"
        # total download time in seconds
        self._dltime = None
        # {"1": 100, ...}
        self._threads_dltime = {}
        # progress bar
        self._progress = Progress(
                TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
                BarColumn(bar_width=None),
                "[progress.percentage]{task.percentage:>3.1f}%",
                "•",
                DownloadColumn(),
                "•",
                TransferSpeedColumn(),
                "•",
                TimeRemainingColumn(),
                )
        self._progress_task_id = None

        logging.info("\nFile Name: {} \nFile Size: {:.2f} MiB \nResumable: {} \nChecksum: {} \nNumber of Threads: {}" \
                .format(self.filename, self.filesize/(1024**2), self.resumable, self.checksum_type, self.num_threads))
    
    @property
    def num_threads(self):
        return self._num_threads

    @num_threads.setter
    def num_threads(self, num_threads):
        if num_threads <= 0:
            raise SystemExit("Number of threads should be a positive integer.")
        if not isinstance(num_threads, int):
            raise SystemExit("Number of threads should be of type integer.")
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
            raise SystemExit("Provided download directory doesn't have enough storage space.")
        elif not os.path.isdir(dldir):
            raise SystemExit("The download directory doesn't exists.")
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
        start_sec = time.perf_counter()

        if self.resumable:
            logging.debug("Starting download in resumable mode.")
            with self._progress:
                self._progress_task_id = self._progress.add_task("download", filename=self.filename, start=False)
                for _ in range(self.num_threads):
                    thread = threading.Thread(target=self.download_chunk)
                    thread.daemon = True
                    thread.start()
                logging.debug("Download threads have been started.")

                self.log_dlstat()
                # wait until all threads are done and the queue is empty
                self.dlqueue.join()
        else:
            logging.debug("Starting download in non-resumable mode.")
            self.nonres_download()
            self.log_dlstat()

        logging.debug("Merging file chunks into single file.")
        with open(self.filepath, "ab") as f:
            for tid in range(self.num_threads):
                chunk_path = os.path.join(self.dldir, self._chunk_filename+str(tid))
                with open(chunk_path) as chunk_file:
                    block = self.lazy_read(chunk_file)
                    f.write(block)

        if self.checksum_type and self.checksum:
            self.check_integrity(self.checksum_type, self.checksum)
        else:
            logging.debug("Checksum not available. skipping integrity check.")

        self.end_time = self.timestamp()
        end_sec = time.perf_counter()
        self._dltime = end_sec - start_sec
        logging.info("Total download time: {}".format(round(self._dltime, 2)))
        if self.resumable:
            for tid in range(self.num_threads):
                thread_avgspeed = (self.filesize/self.num_threads) / self._threads_dltime[str(tid)]
                thread_avgspeed /= 1024**2
                logging.info("Thread: {}, Download Time: {} s, Average Speed: {} MiB/s".format(tid, self._threads_dltime[str(tid)],thread_avgspeed))


    def download_chunk(self):
        """Download each thread chunk."""
        self._progress.update(self._progress_task_id, total=self.filesize)
        while True:
            dljob = self.dlqueue.get()
            try:
                thread_dltime_start = time.perf_counter()
                # update byte range and write mode, if download was interuppted
                if dljob["interrupted"]:
                    time.sleep(1)
                    chunk_path = os.path.join(self.dldir, self._chunk_filename+str(dljob["chunk_id"]))
                    if os.path.isfile(chunk_path):
                        self._write_mode = "ab"
                        orig_chunk_range = dljob["chunk_range"]
                        dljob["chunk_range"] = (orig_chunk_range[0]+os.stat(chunk_path).st_size, orig_chunk_range[1])
                    else:
                        self._write_mode = "wb"

                header = {"Range": "bytes={}-{}".format(*dljob["chunk_range"])}
                with requests.get(self.url, stream=True, verify=self.args.check_certificate, allow_redirects=True, headers=header) as req:
                    req.raise_for_status()
                    chunk_path = os.path.join(self.dldir, self._chunk_filename+str(dljob["chunk_id"]))
                    self._progress.start_task(self._progress_task_id)
                    with open(chunk_path, self._write_mode) as dlf:
                        chunk_size = 1024 * 2
                        for chunk in req.iter_content(chunk_size=chunk_size):
                            if chunk:
                                dlf.write(chunk)
                            self._progress.update(self._progress_task_id, advance=chunk_size)

                thread_dltime_end = time.perf_counter()
                self._threads_dltime[dljob["chunk_id"]] = thread_dltime_end - thread_dltime_start

            except Exception as err:
                logging.error("While downloading chunk with id: {} exception occured: {}.".format(dljob["chunk_id"], err))
                dljob["interrupted"] = True
                self.dlqueue.put(dljob)

            finally:
                self.dlqueue.task_done()


    def nonres_download(self):
        """Download the file in one go, in case server doesn't support resume."""
        try:
            with requests.get(self.url, stream=True, verify=self.args.check_certificate, allow_redirects=True) as req:
                req.raise_for_status()
                with open(self.filepath, "wb") as dlf:
                    chunk_size = 1024**2
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        if chunk:
                            dlf.write(chunk)
        except Exception as err:
            logging.debug("Exception occured during non-resumable download: {}".format(err))
            raise SystemExit("Error while downloading the file: {}".format(err))

    def check_integrity(self, checksum_type, checksum):
        """Check the integrity of downloaded file."""
        if checksum_type == "MD5":
            checksum_md5 = self.get_md5()
            if checksum == checksum_md5:
                logging.debug("MD5 checksum integrity test FAILED.")
                return True
            else:
                logging.debug("MD5 checksum integrity test FAILED.")
                return False
        elif checksum_type == "CRC32C":
            checksum_crc = self.get_crc32()
            if checksum == checksum_crc:
                logging.debug("CRC32 checksum integrity test PASSED.")
                return True
            else:
                logging.debug("CRC32 checkum integrity test FAILED.")
                return False
        elif checksum_type == "CRC32C,MD5":
            header_checksum_crc, header_checksum_md5 = checksum
            file_checksum_crc = self.get_crc32()
            file_checksum_md5 = self.get_md5()
            if (header_checksum_crc==file_checksum_crc) and (header_checksum_md5==file_checksum_md5):
                logging.debug("CRC32 and MD5 checksum integrity test PASSED.")
                return True
            else:
                logging.debug("CRC32 and MD5 checksum integrity test FAILED.")
                return False

    def get_md5(self):
        with open(self.filepath, "rb") as f:
            md5 = hashlib.md5(f.read()).hexdigest
            base64_md5 = base64.b64encode(digest)
        return base64_md5

    def get_crc32(self):
        chunk_size = 1024**2
        with open(self.filepath, "rb") as f:
            thehash = 0
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                thehash = zlib.crc32(chunk, thehash)
        crc = "%08X" % (thehash & 0xFFFFFFFF)
        bas64_crc = base64.b64encode(crc)
        return base64_crc
    
    def log_dlstat(self):
        while not self.isfinished():
            dlstat, total_size = self.dlstat()
            stat_str = "\n"
            for stat in dlstat:
                stat_str += "Part {}: {}%\n".format(*stat)
            logging.info("Download status: {}".format(stat_str))
            time.sleep(5)
        if self.isfinished():
            logging.info("Download complete.")

    def dlstat(self):
        """Get download percentage for each thread."""
        # [(1, 98), (2, 65), ...]
        dlstat = []
        total_size = 0
        for tid in range(self.num_threads):
            chunk_path = os.path.join(self.dldir, self._chunk_filename+str(tid))
            if os.path.isfile(chunk_path):
                chunk_dlsize = os.stat(chunk_path).st_size
                total_size += chunk_dlsize
                chunk_dlperc = round((chunk_dlsize / (self.filesize/self.num_threads)) * 100, 2)
                dlstat.append((tid, chunk_dlperc))
            else:
                dlstat.append((tid, 0.00))
        return dlstat, total_size

    def isfinished(self):
        dlstat, total_size = self.dlstat()
        if total_size == self.filesize:
            return True
        else:
            return False

    def lazy_read(self, fileobj, block_size=1024**2):
        """Generator to read a (big) file in blocks."""
        while True:
            data = fileoj.read(block_size)
            if not data:
                break
            yield data

    def log_speed(self, interval):
        """Log transfer speed every 'interval' seconds."""
        speed_thread = threading.Timer(interval, self.log_speed, args=[interval])
        speed_thread.daemon = True
        speed_thread.start()
        for task in self._progress.tasks:
            speeds = []
            if task.speed:
                speed = round(task.speed, 2)
                speeds.append(speed)
                # self._progress.console.log(speed)
        return speeds


if __name__ == "__main__":
    
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s', level=logging.DEBUG)

    argparser = argparse.ArgumentParser()
    argparser.add_argument("url", help="The url of the file.")
    argparser.add_argument("-d", "--dldir", default=".", help="The download directory. Defualt is CWD.")
    argparser.add_argument("-t", "--nthreads", default=4, type=int, help="Number of threads. Default is 4.")
    argparser.add_argument("--check-certificate", action="store_true", help="Turn on certificate verification.")
    argparser.add_argument("--debug", action="store_true", help="Turn on debug mode.")
    args = argparser.parse_args()

    if not args.debug:
        logging.disable()
    if not args.check_certificate:
        requests.packages.urllib3.disable_warnings()

    xdl = Downloader(args)
    xdl.download()

