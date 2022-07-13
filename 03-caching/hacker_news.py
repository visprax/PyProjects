#!/usr/bin/env python3

"""Using caching mechanism to speed up repetitive tasks."""

import sys
import requests
from bs4 import BeautifulSoup
from cachetools import cached, TTLCache


hacker_news_url = "https://news.ycombinator.com/"
proxies = { 
    'http' : 'socks5h://127.0.0.1:9050',
    'https': 'socks5h://127.0.0.1:9050'
}


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


    return titles

    # mirrors_pool = [link["href"] for link in mirrors_pool]
    # # sort mirrors based on response time
    # mirrors_res_time = []
    # for link in mirrors_pool:
        # try:
            # response = requests.get(link, proxies=proxies)
            # if sort:
                # res_time = response.elapsed.total_seconds()
                # mirrors_res_time.append([link, res_time])
            # else:
                # mirrors_res_time.append(link)
        # except:
            # pass
    # if sort:
        # mirrors_res_time.sort(key=lambda x: x[1])
        # mirrors_pool = [url_res_time[0] for url_res_time in mirrors_res_time]
    # else:
        # mirrors_pool = mirrors_res_time

    # return mirrors_pool


if __name__ == "__main__":
    titles = get_titles(hacker_news_url)
    print(titles)
