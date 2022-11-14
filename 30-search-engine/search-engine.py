#!/usr/bin/env python3

import logging

from utils.data import DataHandler, LazyDataHandler

logger = logging.getLogger("search-engine")


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s')
    logger.setLevel(logging.DEBUG)

    plot_summary_filepath   = Path("data/MovieSummaries/plot_summaries.txt")
    movie_metadata_filepath = Path("data/MovieSummaries/movie.metadata.tsv")

    # data_handler = DataHandler("plot_summaries", plot_summary_filepath)
    # data_handler = LazyDataHandler("plot_summaries", plot_summary_filepath)

    # data_handler = DataHandler("movie_metadata", movie_metadata_filepath)
    data_handler = LazyDataHandler("movie_metadata", movie_metadata_filepath)

    records = data_handler.records()
    print(records[-1])

    # TODO: make these a decorator
    # print these in logging
    # print('Peak Memory Usage =', resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    # print('User Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_utime)
    # print('System Mode Time =', resource.getrusage(resource.RUSAGE_SELF).ru_stime)


