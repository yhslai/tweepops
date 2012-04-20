import tweepy
import pprint
import random
import collections
import re
import requests

api = tweepy.API()
damping_factor = 1

def fetch_followings(user_id, user_graph):
  # if not in cache, fetch them
  if user_id not in user_graph:
    user_graph[user_id] = api.friends_ids(id=user_id)
  return user_graph[user_id]


def get_link(text):
  url_pattern = r'(\bhttp(s)?://[a-zA-Z0-9\-\.]+\.[a-zA-Z]{2,3}(/\S*)?\b)'
  all_matches = re.findall(url_pattern, text)
  return [match[0] for match in all_matches]


def roam(user_id, user_graph, links):
  if random.random() < damping_factor:
    #stop at this user
    timeline = api.user_timeline(id=user_id)
    for status in timeline:
      new_links = get_link(status.text)
      for link in new_links:
        #check if the link is still alive(and resolve the redirections)
        links[link] += status.retweet_count + 1 # the "retweet rank" :)
  else:
    #go to one of following users
    followings = fetch_followings(user.id)
    following = random.choice(followings)
    roam(following, user_graph, links)
    

def start():
  user_graph = {}
  links = collections.defaultdict(int)
  users = [status.user for status in api.public_timeline()]
  while len(links) < 10:
    initial_user = random.choice(users)
    roam(initial_user.id, user_graph, links)
  
  links = links.items()
  links.sort(key=lambda(item): item[1], reverse=True)

  entities = []
  for link, weight in links[:10]:
    response = requests.get(link)
    match = re.search(r'<title>(?P<title>[^<>]*)</title>', response.text)
    title = match.group('title')
    title = re.sub(r'[\n ]+', ' ', title)
    
    entities.append({
      'link': link,
      'weight': weight,
      'title': title,
    })

  for i, entity in enumerate(entities):
    # it looks like "#1: http://to.c/ABCDEFG [5] -- the title of this page"
    print ( "#" + str(i+1) + ": " +
            entity['link'] + " [" + str(entity['weight']) + "] -- " +
            entity['title'] )






