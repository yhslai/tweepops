#!/usr/bin/env python
#coding=utf-8

import tweepy
import pprint
import random
import collections
import re
import requests
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config')
LINKS_LIMIT = config.getint('core', 'links_limit')
DAMPING_FACTOR = config.getfloat('core', 'damping_factor')
LINKS_DISPLAY = config.getint('display', 'links_display')

def reach_limit(api):
  return api.rate_limit_status()['remaining_hits'] == 0

def fetch_followings(api, user_id, user_graph):
  # if not in cache, fetch them
  if user_id not in user_graph:
    user_graph[user_id] = api.friends_ids(id=user_id)
    for friend in user_graph[user_id]:
      user_graph[friend] = []
  return user_graph[user_id]


def get_link(text):
  url_pattern = r'(\bhttp(s)?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?\b)'
  all_matches = re.findall(url_pattern, text)
  return [match[0] for match in all_matches]


def roam(api, user_id, user_graph, links):
  print "Getting Links... ({:d}/{:d})".format(len(links), LINKS_LIMIT)
  if len(links) >= LINKS_LIMIT:
    return

  followings = fetch_followings(api, user_id, user_graph)

  if (not followings) or random.random() < DAMPING_FACTOR:
    #stop at this user
    try:
      timeline = api.user_timeline(id=user_id)
    except tweepy.error.TweepError:
      return

    for status in timeline:
      new_links = get_link(status.text)
      for link in new_links:
        #check if the link is still alive(and resolve the redirections)
        links[link] += status.retweet_count + 1 # the "retweet rank" :)
  else:
    #go to one of following users
    following = random.choice(followings)
    roam(api, following, user_graph, links)
  

def input_first_user(api):
  while True:
    first_user = raw_input("Please input a Twitter username(without @): ")

    try:
      api.get_user(id=first_user)
    except tweepy.error.TweepError:
      print "Sorry there is not '{}' on Twitter!\n".format(first_user)
      continue

    return first_user


def start(api):
  first_user = input_first_user(api)

  user_graph = {}
  chosen_users = set()
  links = collections.defaultdict(int)
  while len(links) < LINKS_LIMIT:
    if reach_limit(api):
      break

    if user_graph:
      if len(chosen_users) == len(user_graph):
        # all users in graph have benn chose as initial user
        print "{}'s friends are too few(or too silent)... try another Twitter username?\n".format(first_user)
        return
      initial_user = random.choice(user_graph.keys())

    else:
      initial_user = first_user 

    roam(api, initial_user, user_graph, links)
    chosen_users.add(initial_user)
  
  print "Parsing..."

  links = links.items()
  links.sort(key=lambda(item): item[1], reverse=True)

  entities = []
  for link, weight in links[:LINKS_DISPLAY]:
    response = requests.get(link)
    match = re.search(r'<title>(?P<title>[^<>]*)</title>', response.text)
    if match:
      title = match.group('title')
      title = re.sub(r'[\n ]+', ' ', title)
    else:
      title = "(unknown)"
    
    entities.append({
      'link': link,
      'weight': weight,
      'title': title,
    })

  print "\nThese are some interesting links chosen for your!\n==================================\n"
  for i, entity in enumerate(entities):
    # it looks like "#1: http://to.c/ABCDEFG [5] -- the title of this page"
    print u"#{:d}: {} [{:d}] -- {}".format(i+1,
                                          entity['link'],
                                          entity['weight'],
                                          entity['title'] )
  print



def input_api_key():
  print "Use Twitter API key you can call Twitter APIs more times."
  do_auth = raw_input("Do you have Twitter API keys?(y/n):")
  if do_auth == 'y':
    consumer_key = raw_input("Consumer Key:")
    consumer_secret = raw_input("Consumer Secret:")
    access_token = raw_input("Access Token:")
    access_token_secret = raw_input("Access Token Secret:")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
  else:
    api = tweepy.API()

  return api



def main():
  api = input_api_key()
      
  while True:
    if reach_limit(api):
      print "Sorry you have reached the Twitter API rate limiting. May retry later?"
      break
    start(api)



main()



