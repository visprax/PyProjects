#!/usr/bin/env python

import twint
import flask
import shutil
import pydeck
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# use caching for retrieval of USA cities online.

# save as json

# users must have a follower threshold for the tweets of that user to be counted. (or maybe verified.)

# c --> conf

# US cities information, including Latitude and Longitude
# usa_cities_data_url = "https://simplemaps.com/static/data/us-cities/1.75/basic/simplemaps_uscities_basicv1.75.zip"

def read_cities(filepath):
    fields = ["city", "lat", "lng"]
    df = pd.read_csv(filepath, usecols=fields)
    return df

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
    

def get_tweets():
    c = twint.Config()

    # c.Format = "ID {id} | Username {username}"
    # c.Store_csv = True
    # c.Output = "tweets.csv"
    # c.Store_pandas = True
    # c.Min_likes = 5
    c.Pandas = True

    # c.Custom["tweet"] = ["id", "date", "place", "geo", "language", "username", "tweet"]


    # c.Username = "noneprivacy"
    # c.Search = "#osint"
    # c.Proxy_host = "127.0.0.1"
    # c.Proxy_port = 9050
    # c.Proxy_type = "socks5"

    # c.Username = "elonmusk"
    c.Search = "biden"
    # c.Lang = "en"
    # c.Translate = True
    # c.TranslateDest = "it"

    c.Near = "San Francisco"
    # c.Geo = "48.880048,2.385939,1km"

    twint.run.Search(c)
    twdf = twint.storage.panda.Tweets_df
    print(twdf.head())

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




if __name__ == "__main__" :

    # print("\n1st statement :")
    # sentence = "Geeks For Geeks is the best portal for \
                # the computer science engineering students."

    # # function calling
    # sentiment_scores(sentence)

    # print("\n2nd Statement :")
    # sentence = "study is going on as usual"
    # sentiment_scores(sentence)

    # print("\n3rd Statement :")
    # sentence = "I am very sad today."
    # sentiment_scores(sentence)
    
    get_tweets()
