# TweePops

A simple CLI application which recommends something interesting on Twitter to you. You can explore the best links someone around you(or your friends, or any Twitterist) shared.

It uses [Twitter API](https://dev.twitter.com) through the excellent [Tweepy](https://github.com/tweepy/tweepy) library. And it sort the recommendation links by **RetweetRank**(just as simplified **PageRank** for Twitter). 

# Installation

    pip install -e .

It's all!

# Usage

    $ ./tweepops
    Do you have Twitter API keys?(y/n):

Then if you have [Twitter API Key](https://dev.twitter.com/apps) you say 'y' and input them. Otherwise just type 'n'.

    Please input a Twitter username(without @): raincolee

**raincolee** is my Twitter username. You can input anyone's username you want.

Wait a minute... and read today's articles/news!

# Caution

If you got this error message:

    Sorry you have reached the Twitter API rate limiting. May retry later?

It's caused by [Twitter Rate Limiting](https://dev.twitter.com/docs/rate-limiting). You can input API Key to extend your limiting(from 150/hour to 350/hour). Or you can descrese the `links_limit` in `config` file.



