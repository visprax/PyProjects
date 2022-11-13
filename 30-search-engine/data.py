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
    def __init__(self, filetype, filepath, progress_bar=False, download_not_exists=True):
        logger.debug(f"starting data handler object with parameters:\n \
                filetype: {filetype}, \n \
                filepath: {filepath}, \n \
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
        self.progress_bar = progress_bar

    def records(self):
        with self.open_file(self.filepath) as f:
            reader = csv.reader(f, delimiter="\t")
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
    def __init__(self, filetype, filepath, progress_bar=False, download_not_exists=True):
        super().__init__(filetype, filepath ,progress_bar, download_not_exists)
        self.num_lines = self.num_lines()

    def records(self):
        rec_gen = self.yield_records(self.filepath)
        # TODO: make it so that we only do it for a specific index of records
        records = [next(rec_gen) for _ in range(self.num_lines)]
        return records

    def yield_records(self, filepath):
        lines = self.get_lines()
        yield from self.process_lines(lines)

    def get_lines(self):
        with open(self.filepath, 'r') as f:
            for line in f:
                yield line

    def process_lines(self, lines, delimiter="\t"):
        for line in lines:
            record = line.strip().split(delimiter)
            yield record

    def num_lines(self):
        def _yield_chunk(reader):
            while True:
                chunk = reader(1024 * 1024)
                if not chunk:
                    break
                yield chunk
        with open(self.filepath, "rb") as f:
            count = sum(buf.count(b"\n") for buf in _yield_chunk(f.raw.read))
        return count



logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
logger.setLevel(logging.DEBUG)
# data_handler = DataHandler("plot_summaries", plot_summary_filepath)
data_handler = LazyDataHandler("plot_summaries", plot_summary_filepath)
# data_handler = DataHandler("movie_metadata", movie_metadata_filepath)
# data_handler = DataHandler("movie_metadata", movie_metadata_filepath)

records = data_handler.records()
print(records[-1])


# TODO: make these a decorator
# print these in logging
# print('Peak Memory Usage =', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
# print('User Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_utime)
# print('System Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_stime)
