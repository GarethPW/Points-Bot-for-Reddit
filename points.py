'''
    Reddit Points Bot v0.1.1

    Created by Reddit user, /u/GarethPW.
    Licensed under GNU General Public License v3.
    www.garethpw.net
'''

from sys import exit as sysexit
if __name__ not in ("__main__","__builtin__"): sysexit();

# === Initialisation ===

import OAuth2Util,os,platform,praw,re,time
from io import open

def info(s,c=0,l=True):
    m = '['+["INFO","WARNING","ERROR"][c]+"] "+s
    #print m
    if l and logging:
        log.write(unicode(time.strftime("[%H:%M:%S] ",time.gmtime()))+unicode(m)+u'\n')

def flush_log():
    if logging:
        log.flush()
        os.fsync(log.fileno())

def calc_votes(points,uppc):
    votes = int(round(points/(2*float(uppc)-1)))
    up = (points+votes)//2
    down = votes-up
    return {'votes': votes,
            'up': up,
            'down': down}
    

logging = True

ver = "0.1.1"
user_agent = platform.system().lower()+":net.garethpw.points:v"+ver+" (by /u/GarethPW)"

footer = u'''

***

*I am a bot and this message was sent automatically.*  
[Subreddit](/r/Points_Bot) | [Creator](/u/GarethPW) | [GitHub](https://github.com/GarethPW/Reddit-Points-Bot)'''

cdata = tuple()
rtype = unicode()
post = unicode()
response = unicode()

# === Log ===

if logging:
    info("Loading points.log...",l=False)
    try:
        log = open("points.log",'a',encoding="utf-8-sig")
    except IOError:
        logging = False
        info("Unable to open points.log. Continuing with logging disabled.",1)
    else:
        log.write(  u'\n'
                   +unicode(time.strftime(u"%Y-%m-%d %H:%M:%S UTC",time.gmtime()))
                   +u'\n'                                                          )
        info("points.log loaded.")
else:
    info("Logging is disabled.")

flush_log()

# === Main Loop ===

reddit = praw.Reddit(user_agent=user_agent)
o = OAuth2Util.OAuth2Util(reddit)
o.refresh(force=True)

info("Initialisation successful.")
flush_log()

for comment in praw.helpers.comment_stream(reddit,"all",limit=100):
    try:
        cdata = re.match(ur"^!(?:(?:Point|Vote)s?|Score)_?Bot(?: (updown|up|down|kys)(?: (this|\w{2,8}))?)?\s*$",comment.body,re.IGNORECASE).groups()
    except AttributeError:
        pass
    else:
        info("Received request! ID: "+str(comment.id)+" Author: "+str(comment.author.name))
        flush_log()
        
        rtype = u"updown" if cdata[0] is None else cdata[0]
        post  = u"this"   if cdata[1] is None else cdata[1]
        
        if rtype == u"kys":
            response = u"fuk u m8 1v1 me on club penguin"
        elif not comment.is_root and post == u"this":
            response = u"Sorry! I can't estimate vote counts for comments."
        else:
            try:
                if post == u"this":
                    post = comment.submission
                else:
                    post = reddit.get_submission(submission_id=post)
            except praw.errors.NotFound:
                response = u"Sorry! It looks like that post doesn't exist."
            else:
                if post.score <= 0 or post.upvote_ratio <= 0.5:
                    response = u"Sorry! This post has too many downvotes to estimate vote counts."
                else:
                    stats = calc_votes(post.score,post.upvote_ratio)
                    
                    response = ( u"Here's my best estimate!\n"
                                +((u"\n* "+unicode(stats['up'   ])+u" upvote"    +(u'' if stats['up'   ] == 1 else u's')) if u"up"     in rtype else u'')
                                +((u"\n* "+unicode(stats['down' ])+u" downvote"  +(u'' if stats['down' ] == 1 else u's')) if u"down"   in rtype else u'')
                                +((u"\n* "+unicode(stats['votes'])+u" total vote"+(u'' if stats['votes'] == 1 else u's')) if u"updown" == rtype else u''))
                    
        comment.reply(response+footer)
