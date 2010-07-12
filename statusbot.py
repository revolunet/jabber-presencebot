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

import settings



class StatusBot(object):
    def __init__(self):
        self.client = xmpp.Client(settings.JABBER_DOMAIN, debug = False )
        self.client.connect( (settings.JABBER_HOST ,settings.JABBER_PORT) )
        self.client.auth(settings.JABBER_USER, settings.JABBER_PWD, 'python')
        self.client.sendInitPresence()
        self.client.RegisterHandler('presence', self.presenceHandler)
        
    def getStatus(self):
        # return a dict containing users and status from roster data
        data = {}
        for jid in self.client.getRoster().getItems():
            status = self.getUserStatus(jid)
            data[jid] = status
        return data
        
    def isAvailable(self, jid):
        # Bool
        roster = self.client.getRoster()
        show = roster.getShow(jid)
        ress =  roster.getResources(jid)
        if len(ress)> 0 and show in [None, 'online', 'available']:
            return True
        return False
        
    def getUserStatus(self, jid):
        return self.isAvailable(jid) and 'online' or 'offline'
    
    def sendMsg(self, jid, msg):
        self.client.send(xmpp.protocol.Message(jid, msg))
        return True
        
    def presenceHandler(self, conn, node):
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

        roster = self.client.getRoster()
        
        
      
            
class HTTPgateway(object):
  started = 0
  def __init__(self, con):
    if HTTPgateway.started == 0:
      thread.start_new_thread(self.webserver, (con, ))
      HTTPgateway.started = 1
      print "HTTPGateway started"
    else:
      self.setConnection(con)
      print "HTTPGateway already started"

  def setConnection(self, con):
    HTTPJabberGateway.jabberCon = con

  def webserver(self, con):
    HTTPJabberGateway.jabberCon = con
    serv = BaseHTTPServer.HTTPServer((settings.HTTP_HOST, settings.HTTP_PORT), HTTPJabberGateway)
    serv.serve_forever()

    
    
    
    
class HTTPJabberGateway(BaseHTTPServer.BaseHTTPRequestHandler):
  jabberCon = None

  def JsonResponse(self, data):
    response = json.dumps(data)
    self.send_response(200)
    self.send_header("Content-type", 'application/json')
    self.send_header("Content-length", len(response))
    self.end_headers()
    self.wfile.write(response)

  def do_GET(self):
    path = self.path[:self.path.find('?')]
    qs = self.path[self.path.find('?')+1:]
    qs = cgi.parse_qs(qs)
    
    #
    # list users and status with JSON
    # /users?pwd=ADMIN_PASSWORD
    # /user/test@revolunet.com?pwd=ADMIN_PASSWORD
    # /send?pwd=ADMIN_PASSWORD&jid=test@revolunet.com&msg=blalab%20balbal
    #
    
    if qs.get('pwd',[''])[0] == settings.ADMIN_PASSWORD:
        if path == '/users':
            data = self.jabberCon.getStatus()
            self.JsonResponse({'users':data})
            
        elif path == '/send':
            jid = qs.get('jid',[''])[0]
            msg = qs.get('msg',[''])[0]
            self.jabberCon.sendMsg( jid, msg)
            self.JsonResponse({'success':True})
            
        elif path.startswith('/user/'):
            paths = path[1:].split('/')
            data = self.jabberCon.getUserStatus(paths[-1])
            self.JsonResponse({'status':data})
        
        
    self.JsonResponse({'success':False})
    return True

def start():
    jabber = StatusBot()
    print 'jabber started %s' % settings.JABBER_USER
    gateway = HTTPgateway(jabber)
    print 'http started port %s' % settings.HTTP_PORT
    while(1):
        try:
              jabber.client.Process(1)
        except Exception, e:
          print "There was an exception - ", e
          traceback.print_exc()
        time.sleep(1)


if __name__ == '__main__':
    start()