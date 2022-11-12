import os
import csv
import ast
import time
import logging
import resource
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("data")


plot_summary_filepath   = Path("data/MovieSummaries/plot_summaries.txt")
movie_metadata_filepath = Path("data/MovieSummaries/movie.metadata.tsv")


def get_line(filepath):
    with open(filepath, 'r') as f:
        for line in f:
            yield line

def process_lines(lines, delimiter="\t"):
    for line in lines:
        record = line.strip().split(delimiter)
        yield record

def get_records(filepath):
    line = get_line(filepath)
    yield from process_lines(line)

""""
start = time.time()
r = get_records(plot_summary_filepath)
end = time.time()
for _ in range(42306):
    print(f"{_}")
    next(r)
print(f"yield execution time: {end-start:.2f}s.")
"""


# print these in logging
# print('Peak Memory Usage =', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
# print('User Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_utime)
# print('System Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_stime)

def datetime_handler(date_string):
    try:
        dt = datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        try:
            dt = datetime.strptime(date_string, "%Y")
        except Exception as err:
            dt = None
    return dt

class DataHandler:
    def __init__(self, filetype, filepath, record_timing=True, progress_bar=False, download_not_exists=True):
        logger.debug(f"starting data handler object with parameters:\n \
                filetype: {filetype}, \n \
                filepath: {filepath}, \n \
                record_timing: {record_timing}, \n \
                progress_bar: {progress_bar}, \n \
                download_not_exists: {download_not_exists}")

        if not filetype in ["plot_summaries", "movie_metadata"]:
            logger.error(f"file type should be either 'plot_summaries' or 'movie_metadata', received: '{filetype}'")
        else:
            self.filetype = filetype

        if not isinstance(filepath, Path):
            logger.error(f"file path should be an instance of pathlib.Path, received: {type(filepath)}")
        elif not filepath.exists() or not filepath.is_file():
            logger.critical(f"file path does not exists or is not a data file, received: {filepath}")
        else:
            self.filepath = filepath
        self.record_timing = record_timing
        self.progress_bar = progress_bar

        if self.record_timing:
            start_time = time.time()
        self.records = self.records()
        if self.record_timing:
            end_time = time.time()
            self.exec_time = f"{end_time - start_time:.3f}s"

    def records(self, delimiter="\t"):
        with self.open_file(self.filepath) as fileobject:
            reader = csv.reader(fileobject, delimiter=delimiter)
            records = self.process_lines(reader)
        return records
    
    def open_file(self, filepath):
        logger.debug(f"opening file: {filepath}")
        logger.info(f"file size: {os.stat(filepath).st_size / (1024 * 1024):.1f} MiB")
        if self.progress_bar:
            import rich.progress
            cm = rich.progress.open(filepath, 'r')
        else:
            cm = open(filepath, 'r')
        return cm
    
    def process_lines(self, reader):
        if self.filetype == "plot_summaries":
            logger.debug("extracting plot summaries...")
            # a list of movie id and summary tuples: (id, summary)
            summaries = [(int(line[0]), line[1]) for line in reader]
            logger.debug("done!")
            return summaries
        if self.filetype == "movie_metadata":
            logger.debug("extracting movie metadata info...")
            # a list of movie metadata tuples:
            # (id, name, release_date, box_office_revenue, runtime, languages, countries, genres)
            metadata = [(int(line[0]), line[2], 
                    # if release_date is empty, make it None, otherwise try to convert it to datetime object
                    (lambda line: None if line[3] == '' else datetime_handler(line[3]))(line),
                    # if revenue or runtime is empty string, instead of converting to float, make it None
                    (lambda line: None if line[4] == '' else float(line[4]))(line), 
                    (lambda line: None if line[5] == '' else float(line[5]))(line), 
                    list(ast.literal_eval(line[6]).values()), 
                    list(ast.literal_eval(line[7]).values()),
                    list(ast.literal_eval(line[8]).values()) 
                ) for line in reader]
            logger.debug("done!")
            return metadata



class LazyDataHandler(DataHandler):
    pass



logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
logger.setLevel(logging.DEBUG)
# data_handler = DataHandler("plot_summaries", plot_summary_filepath)
data_handler = DataHandler("movie_metadata", movie_metadata_filepath)
print(data_handler.records[-1])
print(data_handler.exec_time)

