#!/usr/bin/env python

import re
import twint
import flask
import shutil
import pydeck
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

def read_cities(filepath):
    # universal line ending mode no matter what the file 
    # line ending is, it will all be translated to \n
    with open(filepath, 'rU') as csvfile:
        csvreader = csv.DictReader(csvfile)
        data = {}
        for row in csvreader:
            for header, value in row.items():
                try:
                    data[header].append(value)
                except KeyError:
                    data[header] = [value]
    return data


def download(url, filename):
    import functools
    import pathlib
    import shutil
    import requests
    from tqdm.auto import tqdm

    r = requests.get(url, stream=True, allow_redirects=True)
    if r.status_code != 200:
        r.raise_for_status()  # Will only raise for 4xx codes, so...
        raise RuntimeError(f"Request to {url} returned status code {r.status_code}")
    file_size = int(r.headers.get('Content-Length', 0))

    path = pathlib.Path(filename).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)

    desc = "(Unknown total file size)" if file_size == 0 else ""
    r.raw.read = functools.partial(r.raw.read, decode_content=True)  # Decompress if needed
    with tqdm.wrapattr(r.raw, "read", total=file_size, desc=desc) as r_raw:
        with path.open("wb") as f:
            shutil.copyfileobj(r_raw, f)

    return path


def get_usa_cities(url, zipfile):
    
    chunk_size = 128
    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            fd.write(chunk)

    # shutil.unpack_archive(zipfile, extract_dir="data/cities", format="zip")
    with ZipFile('sampleDir.zip', 'r') as zipObj:
       # Get a list of all archived file names from the zip
       listOfFileNames = zipObj.namelist()
       # Iterate over the file names
       for fileName in listOfFileNames:
           # Check filename endswith csv
           if fileName.endswith('.csv'):
               # Extract a single file from zip
               zipObj.extract(fileName, 'temp_csv')
    


def remove_pattern(string, pattern):
    r = re.findall(pattern, string)
    for i in r:
        string = re.sub(i, '', string)
    return string

def clean_tweet(tweet):
    # remove retweet handles (RT @xyz:)
    tweet = remove_pattern(tweet, "RT @[\w]*:")
    # remove twitter handles (@xyz)
    tweet = remove_pattern(tweet, "@[\w]*")
    # remove url links
    tweet = remove_pattern(tweet, "http?://[A-Za-z0-9./]*")
    # remove special characters, punctuations,... (except for #)
    tweet = lambda tweet: re.sub("[^a-zA-Z0-9#]", ' ', tweet)

    return tweet




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


def get_tweets(city, result, idx):
    c = twint.Config()

    c.Custom["tweet"] = ["id", "date", "time", "near", "language", "username", "tweet"]
    c.Store_csv = True
    c.Output = "tweets.csv"
    c.Lang = "en"

    # c.Username = "elonmusk"
    c.Search = "biden"
    # c.Lang = "en"
    # c.Translate = True
    # c.TranslateDest = "it"

    c.Near = city
    # c.Location = True
    # c.Geo = "48.880048,2.385939,1km"
    
    c.Min_likes = 10
    c.Min_retweets = 5
    c.Min_replies = 2
    
    c.Limit = 20
    c.Hide_output = True
    c.Store_object = True
    tweets = []
    c.Store_object_tweets_list = tweets


    twint.run.Search(c)
    
    # tweets_obj = twint.output.tweets_list

    result[idx] = tweets

    # return tweets


if __name__ == "__main__" :

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


class TWScraper:
    def __init__(self, query, city=None, store=False, num_threads=4, num_processes=4):
        self._query = query
        self._city = city
        self._store = store
        self._num_threads = num_threads
        self._num_processes = num_processes
        self.tweets = []

        self.scrape()

    def scrape(self):
        config = twint.Config()

        config[Custom] = ["id", "data", "time", "near", \
                "language", "username", "tweet"]
        config.Lang = "en"
        config.Search = "{self._query}"
        if self._city:
            config.Near = "{self._city}"
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

    def polish_all(self):
        pool = Pool(self._num_processes)
        self.tweets = pool.map(self.polish, self.tweets)
        

    def polish(self, tweet):
        # retweets handles (RT @xyz), handles (@xyz), links, special chars
        patterns = ["RT @[\w]*:", "@[\w]*", "http?://[A-Za-z0-9./]*", "[^a-zA-Z0-9#]"]
        for pattern in patterns:
            tweet = re.sub(pattern, '', tweet)
        return tweet

