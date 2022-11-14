import os
import csv
import ast
import time
import logging
import resource
from pathlib import Path
from datetime import datetime

logger = logging.getLogger("data")

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
                    (lambda line: None if line[3] == '' else self.datetime_handler(line[3]))(line),
                    # if revenue or runtime is empty string, instead of converting to float, make it None
                    (lambda line: None if line[4] == '' else float(line[4]))(line), 
                    (lambda line: None if line[5] == '' else float(line[5]))(line), 
                    list(ast.literal_eval(line[6]).values()), 
                    list(ast.literal_eval(line[7]).values()),
                    list(ast.literal_eval(line[8]).values()) 
                ) for line in reader]
            logger.debug("done!")
            return metadata
    
    @staticmethod
    def datetime_handler(date_string):
        try:
            dt = datetime.strptime(date_string, "%Y-%m-%d")
        except ValueError:
            try:
                dt = datetime.strptime(date_string, "%Y")
            except Exception as err:
                dt = None
        return dt


class LazyDataHandler(DataHandler):
    def __init__(self, filetype, filepath, progress_bar=False, download_not_exists=True):
        super().__init__(filetype, filepath ,progress_bar, download_not_exists)
        self.num_lines = self.num_lines()

    def records(self):
        logger.debug("yielding records...")
        rec_gen = self.yield_records(self.filepath)
        # TODO: make it so that we only do it for a specific index of records
        records = [next(rec_gen) for _ in range(self.num_lines)]
        logger.debug("done!")
        return records

    def yield_records(self, filepath):
        lines = self.get_lines()
        yield from self.process_lines(lines)

    def get_lines(self):
        with open(self.filepath, 'r') as f:
            for line in f:
                yield line

    def process_lines(self, lines, delimiter="\t"):
        if self.filetype == "plot_summaries":
            for line in lines:
                record = line.strip().split(delimiter)
                # a list of movie id and summary tuples: (id, summary)
                summary = (int(record[0]), record[1])
                yield summary
                
        if self.filetype == "movie_metadata":
            for line in lines:
                record = line.strip().split(delimiter)
                # a list of movie metadata tuples:
                # (id, name, release_date, box_office_revenue, runtime, languages, countries, genres)
                metadata = (int(record[0]), record[2], 
                        # if release_date is empty, make it None, otherwise try to convert it to datetime object
                        (lambda record: None if record[3] == '' else self.datetime_handler(record[3]))(record),
                        # if revenue or runtime is empty string, instead of converting to float, make it None
                        (lambda record: None if record[4] == '' else float(record[4]))(record), 
                        (lambda record: None if record[5] == '' else float(record[5]))(record), 
                        list(ast.literal_eval(record[6]).values()), 
                        list(ast.literal_eval(record[7]).values()),
                        list(ast.literal_eval(record[8]).values()))
                yield metadata

    def num_lines(self):
        logger.debug("counting number of lines in the data file using a buffered generator")
        def _yield_chunk(reader):
            while True:
                chunk = reader(1024 * 1024)
                if not chunk:
                    break
                yield chunk
        with open(self.filepath, "rb") as f:
            count = sum(buf.count(b"\n") for buf in _yield_chunk(f.raw.read))
        logger.info(f"number of lines: {count}")
        return count

