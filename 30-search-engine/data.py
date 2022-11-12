import os
import csv
import ast
import time
import logging
import resource
import rich.progress
from pathlib import Path
from datetime import datetime


plot_summary_filepath   = Path("data/MovieSummaries/plot_summaries.txt")
movie_metadata_filepath = Path("data/MovieSummaries/movie.metadata.tsv")

plot_summary_filesize   = os.stat(plot_summary_filepath).st_size
movie_metadata_filesize = os.stat(movie_metadata_filepath).st_size


def datetime_handler(date_string):
    try:
        dt = datetime.strptime(date_string, "%Y-%m-%d")
    except ValueError:
        try:
            dt = datetime.strptime(date_string, "%Y")
        except Exception as err:
            dt = None
    return dt

if not plot_summary_filepath.exists():
    # download and warn
    pass

start = time.time()

# with plot_summary_filepath.open() as plot_file:
with rich.progress.open(plot_summary_filepath) as plot_file:
    reader = csv.reader(plot_file, delimiter="\t")
    # a list of movie id and summary tuples: (id, summary)
    summaries = [(int(line[0]), line[1]) for line in reader]

    
# with movie_metadata_filepath.open() as metadata_file:
with rich.progress.open(movie_metadata_filepath) as metadata_file:
    reader = csv.reader(metadata_file, delimiter="\t")
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

end = time.time()
print(f"main execution time: {end-start:.2f}s.")

# print(summaries[:5])
# print(metadata[:2])

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


start = time.time()
r = get_records(plot_summary_filepath)
end = time.time()
for _ in range(42306):
    print(f"{_}")
    next(r)
print(f"yield execution time: {end-start:.2f}s.")


# print these in logging
print('Peak Memory Usage =', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
print('User Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_utime)
print('System Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_stime)

class DataHandler:
    def __init__(self, filepath, progress_bar=False, record_timings=True):
        self.filepath = filepath
        self.progress_bar = progress_bar
        self.record_timings = record_timings

    def process_lines(self):
        summaries = [(int(line[0]), line[1]) for line in self.reader]


class LazyDataHandler:

