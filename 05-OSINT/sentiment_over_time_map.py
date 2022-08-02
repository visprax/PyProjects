#!/usr/bin/env python

import os
import re
import csv
import twint
import flask
import shutil
import pydeck
import logging
import requests
from tqdm import tqdm
from threading import Thread
from multiprocessing import Pool
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


# use caching for retrieval of USA cities online.

# use logging instead of prints

# users must have a follower threshold for the tweets of that user to be counted. (or maybe verified.)

# remove tweets with less than 3 characters.

# US cities information, including Latitude and Longitude
# usa_cities_data_url = "https://simplemaps.com/static/data/us-cities/1.75/basic/simplemaps_uscities_basicv1.75.zip"

# use zip to iterate over "city", "lat", and "lng" lists
# use map to apply a function to list
# map(lambda x: x.upper(), cities)


class CityParser:
    def __init__(self, url):
        self._url = url
        self._dir = "./data/city"
        self.data = {}

        self._filename, self._filepath = self.download()
        self.data = self.cities()

    def download(self):
        try:
            listdir = os.listdir(self._dir)
            if not len(listdir) == 0:
                filename = listdir[0]
                filepath = os.path.join(self._dir, filename)
                return filename, filepath 
        except:
            pass
            
        header = requests.head(self._url, allow_redirects=True)
        if header.status_code != 200:
            header.raise_for_status()
            raise SystemExit(f"Could not connect to data server. Returned status code: {req.status_code}")
        try:
            filesize = int(header.headers["Content-Length"])
        except KeyError:
            filesize = None

        try:
            filename = header.headers["Content-Disposition"]
        except KeyError:
            filename = os.path.basename(self._url)
        
        if not os.path.exists(self._dir):
            os.makedirs(self._dir)
        filepath = os.path.join(self._dir, filename)

        print("Downloading: {}".format(filename))
        response = requests.get(self._url, stream=True, allow_redirects=True)
        blocksize = 1024
        progress_bar = tqdm(total=filesize, unit="iB", unit_scale=True)
        with open(filepath, "wb") as dlfile:
            for data in response.iter_content(blocksize):
                progress_bar.update(len(data))
                dlfile.write(data)
        progress_bar.close()
        if progress_bar.n != filesize:
            raise RuntimeError("Error occured during download.")

        return filename, filepath

    def cities(self):
        try:
            files = os.listdir(self._dir)
            if len(files) == 1 and files[0].endswith(".zip"):
                print(f"Unpacking {self._filename}")
                shutil.unpack_archive(self._filepath, extract_dir=self._dir, format="zip")
        except Exception as err:
           raise RuntimeError("Error occured during unzipping the city data: {}".format(err))

        self._csvfile = os.path.join(self._dir, "uscities.csv")
        print("Loading cities information.")
        # universal line ending mode no matter what the file 
        # line ending is, it will all be translated to \n
        with open(self._csvfile, 'r') as csvfile:
            csvreader = csv.DictReader(csvfile)
            data = {}
            for row in csvreader:
                for key, value in row.items():
                    try:
                        data[key].append(value)
                    except KeyError:
                        data[key] = [value]
        return data


class TWScraper:
    def __init__(self, query, limit=20, num_processes=os.cpu_count(), city=None, store=False, clean=False):
        self._query = query
        self._limit = limit
        self._num_processes = num_processes
        self._city = city
        self._store = store
        self._clean = clean
        self._savedir = "./data/tweets"
        os.makedirs(self._savedir, exist_ok=True)
        self.tweets = []

        self.scrape()
        if self._clean:
            self.clean()
   
    @property
    def num_processes(self):
        return self._num_processes
    
    @num_processes.setter
    def num_processes(self, num_processes):
        self._num_processes = num_processes

    def scrape(self):
        config = twint.Config()

        config.Lang = "en"
        config.Search = f"{self._query}"
        if self._city:
            config.Near = f"{self._city}"
        if self._store:
            config.Store_csv = True
            if self._city:
                config.Output = os.path.join(self._savedir, f"{self._city}.csv")
            else:
                config.Output = os.path.join(self._savedir, f"tweets.csv")

        config.Min_likes = 10
        config.Min_retweets = 5
        config.Min_replies = 2

        config.Limit = self._limit
        config.Hide_output = True
        config.Store_object = True
        config.Store_object_tweets_list = self.tweets

        twint.run.Search(config)

    def clean(self):
        pool = Pool(self._num_processes)
        self.tweets = pool.map(self.sub, self.tweets)
        pool.close()

    def sub(self, tweetobj):
        # retweets handles (RT @xyz), handles (@xyz), links, special chars
        patterns = ["RT @[\w]*:", "@[\w]*", "http?://[A-Za-z0-9./]*", "[^a-zA-Z0-9#]"]
        for pattern in patterns:
            tweetobj.tweet = re.sub(pattern, ' ', tweetobj.tweet)
        return tweetobj


def scrape_tweets(cities):
    query = "Biden"
    count = 0
    total = len(cities)
    for city in cities:
        count += 1
        print(f"Running search on twitter for {query} in {city} ({count}/{total}).", end="\r")
        scraper = TWScraper(query, city=city, store=True)


def tweets_from_csv(filepath):
    tweets = []
    with open(filepath, 'r') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            tweets.append(row)
    return tweets


def read_tweets(tweetsdir="./data/tweets"):
    # {"New York": [...], "Los Angeles": [...], ...}
    tweets = {}
    tweets_csvfiles = os.listdir(tweetsdir)
    for csvfile in tweets_csvfiles:
        filepath = os.path.join(tweetsdir, csvfile)
        city_tweets = tweets_from_csv(filepath)
        # name of the file without the .csv extension 
        # (file names are based on city names)
        city_name = os.path.basename(os.path.splitext(csvfile)[0])
        tweets[city_name] = city_tweets
    return tweets


def sentiment(tweet):
    sid_obj = SentimentIntensityAnalyzer()
    # polarity_scores method of SentimentIntensityAnalyzer 
    # object gives a sentiment dictionary, which contains 
    # pos, neg, neu, and compound scores.
    sentiment_dict = sid_obj.polarity_scores(tweet)
    # we use the compound measure as our sentiment score
    sentiment_score = sentiment_dict["compound"]
    return sentiment_score



if __name__ == "__main__":
    cities_url = "https://simplemaps.com/static/data/us-cities/1.75/basic/simplemaps_uscities_basicv1.75.zip"
    city_data = CityParser(cities_url).data
    cities = city_data["city"]
    lats = city_data["lat"]
    lngs = city_data["lng"]
    
    tweetsdir = "./data/tweets"
    try:
        tweets_csvfiles = os.listdir(tweetsdir)
    except Exception as err:
        tweets_csvfiles = []

    if tweets_csvfiles:
        tweets = read_tweets(tweetsdir)
    else:
        # we have a I/O bound problem (waiting for the scraper) so we use 
        # threads instead of processes. If we had CPU bound problem we 
        # would've used processes, like we did for polishing tweets.
        cities = cities[:4]
        num_threads = os.cpu_count()
        threads = [None] * num_threads
        tweets = [None] * num_threads
        range_size = len(cities) / num_threads
        for tidx in range(num_threads):
            city_range = cities[int(tidx*range_size): int((tidx+1)*range_size)]
            threads[tidx] = Thread(target=scrape_tweets, args=[city_range])
            threads[tidx].start()
        for tidx in range(num_threads):
            threads[tidx].join()
        tweets = read_tweets(tweetsdir)

    

    # pool = Pool(os.cpu_count())
    # tweets_sentiment = pool.map(sentiment, tweets)

    print(tweets)
    # print(tweets["Chicago"])

    # plot_data = [(lat, lng, score), ...]



