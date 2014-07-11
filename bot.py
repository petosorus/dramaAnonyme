import tweepy
import os
from time import sleep
from random import randrange

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
	
if __name__ == "__main__":
	#retCode = daemonize()
	cur_dir = os.path.dirname(os.path.realpath(__file__))
	
	api = twitter_authentification(cur_dir + "/keys.conf")
	dms = api.direct_messages()
	first_dm_id = dms[0].id
	start = 0
	while 1:
		try:
			followers = api.followers()				
			for follower in followers:
				if not follower.following:
					follower.follow()
	
		
			if len(dms) > 0:
				print "picking dm"
				picked_dm = dms[randrange(len(dms))]
				dms.remove(picked_dm)
				print picked_dm.text
				api.update_status(picked_dm.text)
				if start < 10:
					start += 1
				
				last_dm_id = dms[len(dms) - 1]	
				first_dm_id = last_dm_id

			print "sleeping"
			if start <= 10:
				print "lucky"
				sleep(300)
			else:
				sleep(3600)
			dms = api.direct_messages(first_dm_id)
		except (tweepy.error.TweepError,IndexError):pass
	
	
	
	
	
