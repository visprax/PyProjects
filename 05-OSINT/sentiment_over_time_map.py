#!/usr/bin/env python

import twint
import keplergl
import flask
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def get_tweets():
    c = twint.Config()

    # c.Username = "noneprivacy"
    # c.Search = "#osint"
    # c.Proxy_host = "127.0.0.1"
    # c.Proxy_port = 9050
    # c.Proxy_type = "socks5"

    # c.Username = "elonmusk"
    c.Search = "biden"
    c.Near = "San Francisco"

    twint.run.Search(c)

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
