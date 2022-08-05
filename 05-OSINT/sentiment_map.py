#!/usr/bin/env python

import os
import re
import csv
import twint
import flask
import shutil
import logging
import datetime
import requests
import keplergl
from tqdm import tqdm
from threading import Thread
from multiprocessing import Pool
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# TODO: use logging instead of prints


class CityParser:
    def __init__(self, url):
        self._url = url
        self._dir = "./data/cities"
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
        self._savedir = os.path.join("./data/tweets")
        os.makedirs(self._savedir, exist_ok=True)
        self._filepath = os.path.join(self._savedir, f"{self._city}.csv")
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
                config.Output = self._filepath
            else:
                config.Output = os.path.join(self._savedir, f"tweets.csv")
        
        # retrieve tweets at most from two week ago
        # config.Since = str(datetime.date.today() - datetime.timedelta(days=14))

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


def sentiment_score(tweet):
    sid_obj = SentimentIntensityAnalyzer()
    # polarity_scores method of SentimentIntensityAnalyzer 
    # object gives a sentiment dictionary, which contains 
    # pos, neg, neu, and compound scores.
    sentiment_dict = sid_obj.polarity_scores(tweet)
    # we use the compound measure as our sentiment score
    sentiment_score = sentiment_dict["compound"]
    return sentiment_score

def tweets_sentiment(cities_info, num_threads, thread_index):
    range_size = len(cities_info) / num_threads
    cities_range = cities_info[int(thread_index*range_size): int((thread_index+1)*range_size)]
    query = "Biden"
    count = 0
    total = len(cities_info)
    for city_dict in cities_range:
        count += 1
        city = city_dict["city"]
        print(f"Running search on twitter for {query} in {city} ({count}/{total}).")
        scraper = TWScraper(query, limit=20, city=city, store=True)
        city_tweets = [tweet_obj.tweet for tweet_obj in scraper.tweets]
        if city_tweets:
            city_sentiments = list(map(sentiment_score, city_tweets))
            average_city_sentiment = sum(city_sentiments) / len(city_sentiments)
            city_dict.update({"sentiment": round(average_city_sentiment, 3)})

def get_cities_info(cities_url):
    # data is in the descending order of the population of the city 
    city_data = CityParser(cities_url).data
    cities = city_data["city"]
    lats = city_data["lat"]
    lngs = city_data["lng"]
    counties = city_data["county_name"]
    # we consider cities which have population greater than this amount
    population_cutoff = 10000
    cutoff_index = next(x[0] for x in enumerate(list(map(int, city_data["population"]))) if x[1] < population_cutoff)
    cities = cities[:cutoff_index]
    lats = lats[:cutoff_index]
    lngs = lngs[:cutoff_index]
    counties = counties[:cutoff_index]
    num_cities = len(cities)
    cities_info = [{"city": cities[i], "latitude": lats[i], "longitude": lngs[i], "county": counties[i], "sentiment": None} for i in range(num_cities)]
    return cities_info

def run_scrapers(cities_info, sentiment_filepath, num_threads=os.cpu_count(), fresh=True):
    if fresh:
        # we have a I/O bound problem (waiting for the scraper) so we use 
        # threads instead of processes. If we had CPU bound problem we 
        # would've used processes, like we did for polishing tweets.
        threads = [None] * num_threads
        for thread_index in range(num_threads):
            threads[thread_index] = Thread(target=tweets_sentiment, args=[cities_info, num_threads, thread_index])
            threads[thread_index].start()
        for thread_index in range(num_threads):
            threads[thread_index].join()
    else:
        if not os.path.isfile(sentiment_filepath):
            raise SystemExit("The sentiment file doesn't exist.")
        cities_info = []
        with open(sentiment_filepath, 'r') as sentiment_file:
            reader = csv.DictReader(sentiment_file)
            for row in reader:
                cities_info.append(row)
    return cities_info

def plot(cities_info):
    latlng = [[city_dict["latitude"], city_dict["longitude"]] for city_dict in cities_info]
    view = view = pdk.data_utils.compute_view(latlng)
    view.zoom = 6
    layer = pydeck.Layer(
            "HeatmapLayer", 
            data=cities_info,
            auto_highlight=True,
            get_position=["latitude", "longitude"],
            get_weight="sentiment",
            pickable=True,
            )
    view_state = pdk.ViewState(
            longitude=-73.924, 
            latitude=40.69, 
            zoom=6, 
            min_zoom=5,
            max_zoom=15,
            pitch=40.5,
            bearing=-27.36
            )
    render = pydeck.Deck(layers=[layer], initial_view=view_state)
    render.to_html("sentiments_map.html")

def get_counties_info(cities_info):
    # unqiue counties
    counties = list(set([city_dict["county"] for city_dict in cities_info]))
    # calculate counties average sentiment
    counties_sentiment = [{"county": counties[i], "sentiment": None} for i in range(len(counties))]
    for county in counties:
        sentiments = []
        for city_dict in cities_info:
            if city_dict["county"] == county:
                sentiment = city_dict["sentiment"]
                if sentiment:
                    sentiments.append(city_dict["sentiment"])
        if sentiments:
            average_county_sentiment = sum(sentiments) / len(sentiments)
        else:
            average_city_sentiment = None
        for county_dict in counties_sentiment:
            if county_dict["county"] == county:
                county_dict["sentiment"] = average_city_sentiment
    return counties_sentiment


if __name__ == "__main__":
    # US cities information, including Latitude and Longitude
    cities_data_url = "https://simplemaps.com/static/data/us-cities/1.75/basic/simplemaps_uscities_basicv1.75.zip"
    cities_info = get_cities_info(cities_data_url)
    cities_info = cities_info[:4]

    sentiment_dir = os.path.join("./data/sentiments/")
    sentiment_filepath = os.path.join(sentiment_dir, "sentiments.csv")
    cities_info = run_scrapers(cities_info, sentiment_filepath)
    counties_sentiment = get_counties_info(cities_info)

    # save the results
    os.makedirs(sentiment_dir, exist_ok=True)
    with open(sentiment_filepath, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(cities_info[0].keys()))
        writer.writeheader()
        writer.writerows(cities_info)

    plot(cities_info)

