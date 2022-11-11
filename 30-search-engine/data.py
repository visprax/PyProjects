#!/usr/bin/env python3

import csv
import ast
from pathlib import Path


plot_summary_filepath   = Path("data/MovieSummaries/plot_summaries.txt")
movie_metadata_filepath = Path("data/MovieSummaries/movie.metadata.tsv")

if not plot_summary_filepath.exists():
    # download and warn
    pass

with plot_summary_filepath.open() as plot_file:
    reader = csv.reader(plot_file, delimiter="\t")
    # a list of movie id and summary tuples, (id, summary)
    summaries = [(line[0], line[1]) for line in reader]

    
with movie_metadata_filepath.open() as metadata_file:
    reader = csv.reader(metadata_file, delimiter="\t")
    # a list of movie metadata tuples,
    # (id, name, release_data, box_office_revenue, runtime, languages, countries, genres)
    metadata = [(line[0], line[2], line[3], line[4], line[5], 
            list(ast.literal_eval(line[6])), 
            list(ast.literal_eval(line[7])),
            list(ast.literal_eval(line[8])) 
        )]
