#!/usr/bin/env python3

""" Parse Hacker News titles into a minimalistic list in terminal.
We demonstrate caching mechanism to speed up repetitive tasks.
"""

import sys
import requests
from time import time
from bs4 import BeautifulSoup
from cachetools import cached, TTLCache
from rich.console import Console
from rich.table import Table

cache = TTLCache(maxsize=100, ttl=500)

hacker_news_url = "https://news.ycombinator.com/"
proxies = { 
    'http' : 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}

def timer(func):
    """Time the exection of functions."""
    def wrap_func(*args, **kwargs):
        t1 = time()
        result = func(*args, **kwargs)
        t2 = time()
        print("Execution time of {}: {:.4f}s".format(func.__name__, (t2-t1)))
        return result

    return wrap_func

@timer
@cached(cache)
def get_titles(url, proxy=False):
    try:
        if proxy:
            page = requests.get(url, timeout=10, proxies=proxies)
        else:
            page = requests.get(url, timeout=10)
        soup = BeautifulSoup(page.content, "html.parser")
        title_tags = soup.find_all('a', {"class":"titlelink"})
        titles = [(title.text, title["href"]) for title in title_tags]
        return titles

    except:
        try:
            page = requests.get(url, timeout=10, proxies=proxies)
            soup = BeautifulSoup(page.content, "html.parser")
            title_tags = soup.find_all('a', {"class":"titlelink"})
            titles = [(title.text, title["href"]) for title in title_tags]
            return titles
        except Exception as err:
            print("Couldn't connect to {}. Exception '{}' occured.".format(url, err))
            sys.exit(1)

    return None

def display_titles(titles):
    console = Console()

    table = Table(show_header=False, show_lines=True)
    table.add_column("Title")
    for title in titles:
        table.add_row("{}".format(title[0]), style="link {}".format(title[1]))

    console.print(table)


@timer
def many_requests(count=10):
    for _ in range(count):
        titles = get_titles(hacker_news_url)
    
    return titles

if __name__ == "__main__":
    titles = get_titles(hacker_news_url)
    many_requests()

    display_titles(titles)
