#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tweepy
import os
from time import sleep
from random import randrange
import re
from time import localtime

def file_to_dict(file_name):
	"""opens a file and put tab separated values in a dict"""
	f = open(file_name, 'r')
	d_keys = {}
	for i in f.readlines():
		i = i[:len(i) - 1]		#Removing the \n char
		j = i.split('\t')
		d_keys[j[0]] = j[1]
	return d_keys

def twitter_authentification(keys_file):
	"""return a tweepy.api object connected to your account"""
	d_keys = file_to_dict(keys_file)
	auth = tweepy.OAuthHandler(d_keys["consumer_key"], 
		d_keys["consumer_secret"])
	auth.set_access_token(d_keys["access_token"], 
		d_keys["access_secret"])
	api = tweepy.API(auth)
	return api

def daemonize():
    try:
        pid = os.fork()
    except OSError, e:
        raise Exception, "%s [%d]" % (e.argsstrerror, e.argserrno)
    if (pid == 0):      # Ayanami Rei
        os.setsid()
        try:
            pid = os.fork()
        except OSError, e:
            raise Exception, "%s [%d]" % (e.argsstrerror, e.argserrno)
        if (pid == 0):      # Langley Soryu Asuka
            os.chdir("/")
            os.umask(0)
        else:
            os._exit(0)
    else:
        os._exit(0)
    os.open("/dev/null",os.O_RDWR)
    os.dup2(0,1)
    os.dup2(0,2)
    print pid
    return(0)

def is_direct_mention(text):
	pattern_direct_mention = re.compile("^@.+")
	return re.match(pattern_direct_mention, text)
	
def contains_link(text):
	pattern_link = re.compile(".*?http.*?")
	return re.match(pattern_link, text)

def parsing_dm_list(dm_list):
	dm_list_copy = []
	for dm in dm_list:
		if not is_direct_mention(dm.text) and not contains_link(dm.text):
			dm_list_copy.append(dm)
	return dm_list_copy
	
def display_time():
	time = localtime()
	return str(time[3]) + "h" + str(time[4]) + "min"
	
def logging_tweets(dm):
	f = open("tweets.log", 'a')
	f.write(dm.text + "\t" + dm.sender.screen_name)
	f.close()
	
if __name__ == "__main__":
	#retCode = daemonize()
	cur_dir = os.path.dirname(os.path.realpath(__file__))
	
	api = twitter_authentification(cur_dir + "/keys.conf")
	dms = api.direct_messages()
	dms = parsing_dm_list(dms)

	while 1:
		try:
			print "Nb de DM : " + str(len(dms))
			print "Follow back"
			followers = api.followers()				
			for follower in followers:
				if not follower.following:
					try:
						follower.follow()
					except tweepy.error.TweepError:pass
			
			print "sleeping before tweeting : " + display_time()
			sleep(1800)
		
			if len(dms) != 0:
				print "Picking dm"
				picked_dm = dms[randrange(len(dms))]
				logging_tweets(picked_dm)	
				dms.remove(picked_dm)
				api.destroy_direct_message(picked_dm.id)
				print picked_dm.text
				api.update_status(picked_dm.text)
				
				last_dm_id = dms[len(dms) - 1]	
				first_dm_id = last_dm_id

			print "sleeping before following : " + display_time()
			sleep(1800)
			
			try:
				dms = api.direct_messages(first_dm_id)
				dms = parsing_dm_list(dms)
			except tweepy.error.TweepError:pass
		except IndexError:pass
	
	
	
	
