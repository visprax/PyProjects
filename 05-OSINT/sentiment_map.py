#!/usr/bin/env python

import os
import re
import csv
import json
import twint
import shutil
import logging
import datetime
import requests
from tqdm import tqdm
from flask import Flask
from threading import Thread
from keplergl import KeplerGl
from multiprocessing import Pool
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


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
                logging.info(f"Unpacking {self._filename}")
                shutil.unpack_archive(self._filepath, extract_dir=self._dir, format="zip")
        except Exception as err:
           raise RuntimeError("Error occured during unzipping the city data: {}".format(err))

        self._csvfile = os.path.join(self._dir, "uscities.csv")
        logging.info(f"Loading '{self._csvfile}'")
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
    total = len(cities_range)
    for city_dict in cities_range:
        count += 1
        city = city_dict["city"]
        logging.info(f"Running search on twitter for {query} in {city} ({count}/{total})")
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
    counties_fips = city_data["county_fips"]
    states_id = city_data["state_id"]
    states_name = city_data["state_name"]
    # we consider cities which have population greater than this amount
    population_cutoff = 10000
    cutoff_index = next(x[0] for x in enumerate(list(map(int, city_data["population"]))) if x[1] < population_cutoff)
    for l in [cities, lats, lngs, counties, counties_fips, states_id, states_name]:
        l = l[:cutoff_index]
    num_cities = len(cities)
    cities_info = [{
        "city": cities[i], 
        "latitude": lats[i],
        "longitude": lngs[i], 
        "county": counties[i],
        "county_fips": counties_fips[i], 
        "state_id": states_id[i],
        "state_name": states_name[i],
        "sentiment": None
        } \
        for i in range(num_cities)]
    return cities_info

def get_counties_info(cities_info, fresh=True):
    sentiment_dir = os.path.join("./data/sentiments/")
    counties_sentiment_filepath = os.path.join(sentiment_dir, "counties.csv")
    
    if not fresh and os.path.isfile(counties_sentiment_filepath):
        logging.info(f"File '{counties_sentiment_filepath}' exists. Loading")
        counties_info = read_csv(counties_sentiment_filepath)
        return counties_info
       
    logging.info(f"Constructing counties info.")
    # unqiue county fips codes
    unique_counties = list({city_dict['county_fips']:city_dict for city_dict in cities_info}.values())
    counties_info = [{
        "county": county["county"], 
        "county_fips": county["county_fips"], 
        "state_id": county["state_id"],
        "state_name": county["state_name"],
        "sentiment": None
        } for county in unique_counties]
    # calculate counties average sentiment
    for county_dict in counties_info:
        sentiments = []
        county = county_dict["county"]
        for city_dict in cities_info:
            if city_dict["county"] == county:
                sentiment = city_dict["sentiment"]
                if sentiment:
                    sentiments.append(city_dict["sentiment"])
        if sentiments:
            average_county_sentiment = sum(sentiments) / len(sentiments)
        else:
            average_city_sentiment = None
        county_dict["sentiment"] == average_county_sentiment
    os.makedirs(sentiment_dir, exist_ok=True)
    write_csv(counties_info, counties_sentiment_filepath)
    return counties_info

def run_scrapers(cities_info, num_threads=os.cpu_count(), fresh=True):
    sentiment_dir = os.path.join("./data/sentiments/")
    cities_sentiment_filepath = os.path.join(sentiment_dir, "cities.csv")

    if not fresh and os.path.isfile(cities_sentiment_filepath):
        logging.info(f"File '{cities_sentiment_filepath}' exists, loading")
        cities_info = read_csv(cities_sentiment_filepath)
        return cities_info

    # we have a I/O bound problem (waiting for the scraper) so we use 
    # threads instead of processes. If we had CPU bound problem we 
    # would've used processes, like we did for polishing tweets.
    threads = [None] * num_threads
    for thread_index in range(num_threads):
        threads[thread_index] = Thread(target=tweets_sentiment, args=[cities_info, num_threads, thread_index])
        threads[thread_index].start()
    for thread_index in range(num_threads):
        threads[thread_index].join()
    os.makedirs(sentiment_dir, exist_ok=True)
    write_csv(cities_info, cities_sentiment_filepath)
    return cities_info

def write_csv(data, filepath):
    logging.info(f"Writing '{filepath}'")
    if os.path.isfile(filepath):
        logging.warning(f"File '{filepath}' exists, overriding")
    with open(filepath, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=list(data[0].keys()))
        writer.writeheader()
        writer.writerows(data)

def read_csv(filepath, encoding="utf-8"):
    data = []
    logging.info(f"Reading '{filepath}'")
    if os.path.isfile(filepath):
        with open(filepath, 'r', encoding=encoding) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                data.append(row)
    else:
        logging.error(f"File '{filepath}' doesn't exists")
    return data

def download(url, filepath):
    if os.path.isfile(filepath):
        logging.warning(f"File '{filepath}' exists, aborting download")
    else:
        try:
            header = requests.head(url, stream=True, allow_redirects=True)
        except Exception as err:
            logging.error(f"Error: {err}, occured during connection to server, while downloading from: {url}")

        try:
            filename = header.headers["Content-Disposition"]
        except:
            filename = os.path.basename(url)

        try:
            filesize = header.headers["Content-Length"]
        except:
            filesize = None

        logging.info(f"Downloading: '{filename}'")
        response = requests.get(url, stream=True, allow_redirects=True)
        blocksize = 1024
        progress_bar = tqdm(total=filesize, unit="iB", unit_scale=True)
        with open(filepath, "wb") as dlfile:
            for data in response.iter_content(blocksize):
                progress_bar.update(len(data))
                dlfile.write(data)
        progress_bar.close()
        if progress_bar.n != filesize:
            logging.critical(f"Error occured during download from {url}")
            raise RuntimeError()

def get_geodata(counties_info, fresh=True):
    json_dir = "./data/json/"
    os.makedirs(json_dir, exist_ok=True)
    geodata_filepath = os.path.join(json_dir, "county_sentiments.geojson")

    if not fresh and os.path.isfile(geodata_filepath):
        logging.info(f"File {geodata_filepath} exists, loading")
        with open(geodata_filepath, 'r') as geofile:
            geodata = json.load(geofile)
        return geodata

    logging.info("Attempting to construct geo data")

    sample_geojson_url = "https://raw.githubusercontent.com/uber-web/kepler.gl-data/master/county_unemployment/data.geojson"
    sample_config_url = "https://raw.githubusercontent.com/uber-web/kepler.gl-data/master/county_unemployment/config.json"
    sample_geojson_filepath = os.path.join(json_dir, "data.geojson")
    sample_config_filepath = os.path.join(json_dir, "config.json")
    urls = [sample_geojson_url, sample_config_url]
    filepathes = [sample_geojson_filepath, sample_config_filepath]
    for url, filepath in zip(urls, filepathes):
        download(url, filepath)
    
    with open(sample_geojson_filepath, 'r') as geofile:
        geodata = json.load(geofile)
    # indices of counties that are in geodata but not in counties_info
    indices = []
    # add sentiment to sample geo json data
    for i in range(len(geodata["features"])):
        props = geodata["features"][i]["properties"]
        county_fips = int(props["GEOID"])
        found = False
        for county in counties_info:
            if int(county["county_fips"]) == county_fips:
                found = True
                new_props = {
                        'NAME': props['NAME'], 
                        'ALAND': props['ALAND'], 
                        'LSAD': props['LSAD'],
                        'AWATER': props['AWATER'],
                        'COUNTYFP': props['COUNTYFP'],
                        'AFFGEOID': props['AFFGEOID'],
                        'GEOID': props['GEOID'],
                        'STATEFP': props['STATEFP'],
                        'COUNTYNS': props['COUNTYNS'],
                        'SENTIMENT': county['sentiment']
                        }
                break
        if found:
            geodata["features"][i]["properties"] = new_props
        else:
            indices.append(i)
    # remove the counties that we have not sentiment data
    for i in sorted(indices, reverse=True):
        del geodata["features"][i]

    # save geo data 
    geodata_filepath = os.path.join(json_dir, "county_sentiments.geojson")
    with open(geodata_filepath, 'w') as geofile:
        json.dump(geodata, geofile)
    return geodata



def plot(geodata):
    sample_config_filepath = os.path.join("./data/json/", "config.json")
    config_filepath = os.path.join("./data/json/", "sentiment_config.json")

    if os.path.isfile(config_filepath):
        logging.info(f"File '{config_filepath}' exists, loading")
        with open(config_filepath, 'r') as conf_file:
            config = json.load(conf_file)
    else:
        logging.info(f"Loading '{sample_config_filepath}'")
        with open(sample_config_filepath, 'r') as conf_file:
            config = json.load(conf_file)
        # replace some values
        config["config"]["visState"]["layers"][0]["config"]["dataId"] = "county_sentiment"
        config["config"]["visState"]["layers"][0]["config"]["label"] = "counties_sentiment"
        config["config"]["visState"]["layers"][0]["visualChannels"]["colorField"]["name"] = "sentiment"
        config["config"]["visState"]["interactionConfig"]["tooltip"]["fieldsToShow"]["jd4v637ja"] = ['NAME', 'SENTIMENT']

        logging.info(f"Writing {config_filepath}")
        with open(config_filepath, 'w') as conf_file:
            json.dump(config, conf_file)

    plot = KeplerGl(data=geodata, config=config)
    return plot


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s  %(name)s  %(levelname)s: %(message)s', level=logging.INFO)

    # US cities information, including Latitude and Longitude
    cities_data_url = "https://simplemaps.com/static/data/us-cities/1.75/basic/simplemaps_uscities_basicv1.75.zip"
    cities_info = get_cities_info(cities_data_url)
    cities_info = cities_info[:4]

    cities_info = run_scrapers(cities_info, fresh=True)
    counties_info = get_counties_info(cities_info, fresh=True)

    geodata = get_geodata(counties_info, fresh=True)
    print(geodata)
    plot = plot(geodata)
