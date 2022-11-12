#!/usr/bin/env python3

import csv
import ast
from pathlib import Path
from datetime import datetime


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

if not plot_summary_filepath.exists():
    # download and warn
    pass

with plot_summary_filepath.open() as plot_file:
    reader = csv.reader(plot_file, delimiter="\t")
    # a list of movie id and summary tuples: (id, summary)
    summaries = [(int(line[0]), line[1]) for line in reader]

    
with movie_metadata_filepath.open() as metadata_file:
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

print(summaries[:2])
print(metadata[:2])
