#!/usr/bin/env python

import os
import re
import tqdm
import twint
import flask
import shutil
import pydeck
import requests
from threading import Thread
from multiprocessing import Pool
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# use caching for retrieval of USA cities online.

# save as json

# users must have a follower threshold for the tweets of that user to be counted. (or maybe verified.)

# remove tweets with less than 3 characters.

# US cities information, including Latitude and Longitude
# usa_cities_data_url = "https://simplemaps.com/static/data/us-cities/1.75/basic/simplemaps_uscities_basicv1.75.zip"

# use zip to iterate over "city", "lat", and "lng" lists
# use map to apply a function to list
# map(lambda x: x.upper(), cities)

# threading to scrape the tweets
# multiprocessing to clean the tweets

# concurrent.futures -> ThreadPoolExecuter, ProcessPoolExecuter




class TWScraper:
    def __init__(self, query, city=None, store=False, num_processes=4):
        self._query = query
        self._city = city
        self._store = store
        self._num_processes = num_processes
        self.tweets = []

        self.scrape()
        self.polish()
   
    @property
    def num_processes(self):
        return self._num_processes
    
    @num_processes.setter
    def num_processes(self, num_processes):
        self._num_processes = num_processes

    def scrape(self):
        config = twint.Config()

        config[Custom] = ["id", "data", "time", "near", \
                "language", "username", "tweet"]
        config.Lang = "en"
        config.Search = f"{self._query}"
        if self._city:
            config.Near = f"{self._city}"
        if self._store:
            config.Store_csv = True
            config.Output = "tweets.csv"

        config.Min_likes = 10
        config.Min_retweets = 5
        config.Min_replies = 2

        config.Limit = 20
        config.Hide_output = True
        config.Store_object = True
        config.Store_object_tweets_list = self.tweets
        twint.run.Search(config)

    def polish(self):
        pool = Pool(self._num_processes)
        self.tweets = pool.map(self.sub, self.tweets)

    def sub(self, tweet):
        # retweets handles (RT @xyz), handles (@xyz), links, special chars
        patterns = ["RT @[\w]*:", "@[\w]*", "http?://[A-Za-z0-9./]*", "[^a-zA-Z0-9#]"]
        for pattern in patterns:
            tweet = re.sub(pattern, '', tweet)
        return tweet


class CityParser:
    def __init__(self, url):
        self._url = url
        self._dir = "./data/city"
        self.data = {}

    def download(self):
        header = requests.head(self._url, allow_redirects=True)
        if header.status_code != 200:
            header.raise_for_status()
            raise SystemExit(f"Could not connect to data server. Returned status code: {req.status_code}")
        try:
            self._filesize = int(header.headers["Content-Length"])
        except KeyError:
            self._filesize = None

        try:
            self._filename = header.headers["Content-Disposition"]
        except KeyError:
            self._filename = os.path.basename(self._url)
        
        if not os.path.exists(self._dir):
            os.makedirs(self._dir)
        self._filepath = os.path.join(self._dir, self._filename)

        req = requests.head(self._url, stream=True, allow_redirects=True)
        desc = "Unknown file size" if not self._filesize else ''
        with tqdm.wrapattr(req.raw, "read", total=self._filesize, desc=desc) as raw:
            with open(self._filepath, "wb") as output:
                shutil.copyfileobj(raw, output)

        return self._filepath

    def cities(self):
        try:
            shutil.unpack_archive(self._filepath, extract_dir=self._dir, format="zip")
        except Exception as err:
           raise RuntimeError("Error occured during unzipping the city data: {}".format(err))

        self._csvfile = os.path.join(self._dir, "uscities.csv")
        # universal line ending mode no matter what the file 
        # line ending is, it will all be translated to \n
        with open(self._csvfile, "rU") as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                for key, value in row.items():
                    try:
                        self.data[key].append(value)
                    except KeyError:
                        self.data[key] = [value]
        return self.data


def sentiment_scores(sentence):

    # Create a SentimentIntensityAnalyzer object.
    sid_obj = SentimentIntensityAnalyzer()

    # polarity_scores method of SentimentIntensityAnalyzer
    # object gives a sentiment dictionary.
    # which contains pos, neg, neu, and compound scores.
    sentiment_dict = sid_obj.polarity_scores(sentence)

    print("Overall sentiment dictionary is : ", sentiment_dict)
    print("sentence was rated as ", sentiment_dict['neg']*100, "% Negative")
    print("sentence was rated as ", sentiment_dict['neu']*100, "% Neutral")
    print("sentence was rated as ", sentiment_dict['pos']*100, "% Positive")

    print("Sentence Overall Rated As", end = " ")

    # decide sentiment as positive, negative and neutral
    if sentiment_dict['compound'] >= 0.05 :
        print("Positive")

    elif sentiment_dict['compound'] <= - 0.05 :
        print("Negative")

    else :
        print("Neutral")




if __name__ == "__main__":
    scraper = TWScraper("biden", city="New York")


    # print("Statement:")
    # sentence = "@POTUS How about this? His own people acknowledged he’s a shithead"
    # print(sentence, '\n')
    # sentiment_scores(sentence)

    NUM_THREADS = 4
    NUM_PROCESS = 4

    cities = ["New York", "Los Angeles", "Chicago", "Miami"]

    threads = [None] * NUM_THREADS
    results = [None]* NUM_THREADS
   
    # we have a  I/O bound problem (waiting for the scraper) so we use 
    # threads instead of processes. if we had CPU bound problem we 
    # would've used processes.
    for i in range(NUM_THREADS):
        threads[i] = Thread(target=get_tweets, args=[cities[i], results, i])
        threads[i].start()

    # tw = get_tweets(city)

    # print(tw[0].near)
    # print(tw[0].tweet)

    for i in range(NUM_THREADS):
        threads[i].join()

    # asyncio.run(get_tweets())
    print(results[1][11].near)

    pool = Pool(NUM_PROCESS)
    tweets = pool.map(clean_tweet, tweets)
