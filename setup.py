#! /usr/bin/env python

from setuptools import setup

setup(
  name="TweePops",
  version="0.0.1",
  description="A very simple app to crawl popular news from Twitter",
  author="Raincole Lai",
  author_email="raincolee@gmail.com",
  install_requires=[
    'requests>=0.11.1',
    'tweepy>=1.9',
  ],
) 

