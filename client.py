import os, sys
import traceback
import time
import re
import glob
import thread
import BaseHTTPServer 
import xmpp
import cgi
import simplejson as json
 
#
# this is a simple jabber client
# can be used to track server status
# todo : add commands : uptime/who/top/uname...

class StatusBotClient(object):
    def __init__(self, jid, password):
        (USER, DOMAIN) = jid.split('@')
        self.client = xmpp.Client( DOMAIN, debug = False ) 
        self.client.connect( (DOMAIN ,5222 ) )
        self.client.auth( USER , password , 'python')
        self.client.sendInitPresence()
       # self.client.RegisterHandler('presence', self.presenceHandler)
 
    def presenceHandler(self, conn, node):
        # handles presences and subscriptions requests
        fromJID = node.getFrom().getStripped()
        presType = node.getType()

        if not presType:
            presType = 'available'
        if fromJID != settings.JABBER_USER:
            if presType == 'subscribe':
                # auto-suscribe
                self.client.sendPresence(jid=fromJID, typ='subscribed')
                self.client.sendPresence(jid=fromJID, typ='subscribe')
            elif presType == 'unsubscribe':
                # auto-unsuscribe
                self.client.sendPresence(jid=fromJID, typ='unsubscribed')
                self.client.sendPresence(jid=fromJID, typ='unsubscribe')

        #roster = self.client.getRoster()
        
        
       
def start(*args):
    
    jabber = StatusBotClient(*args)
    print 'jabber started'
    
    # auto suscribe to BOT
    BOT_JID = 'status@revolunet.com'
    jabber.client.sendPresence(jid = BOT_JID, typ='subscribe')
    jabber.client.sendPresence(jid = BOT_JID, typ='subscribed')
 
    while(1):
        try:
              jabber.client.Process(1)
        except Exception, e:
          print "There was an exception - ", e
          traceback.print_exc()
        time.sleep(1)


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "USAGE: client.py server@jabber.com jabbpassword"
        sys.exit()
    start(sys.argv[1], sys.argv[2])
