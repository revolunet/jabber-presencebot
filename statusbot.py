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
        self.client = xmpp.Client(settings.JABBER_DOMAIN, debug = settings.DEBUG) 
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
        try:
            return self.isAvailable(jid) and 'online' or 'offline'
        except:
            print 'StatusBot getUserStatus EXCEPTION'
            return 'offline'
    
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

  def ImgResponse(self, inImg):
    ext = os.path.splitext(inImg)[1][1:].lower()
    if os.path.realpath(inImg).startswith(os.path.realpath(settings.STATIC_DIR)):
        data = open(inImg, 'rb').read()
        self.send_response(200)
        self.send_header("Content-type", 'image/%s' % ext)
        self.send_header("Content-length", len(data))
        self.end_headers()
        self.wfile.write(data)
    
  def HtmlResponse(self, file):
    context = {
        'JABBER_USER':'%s@%s' % (settings.JABBER_USER, settings.JABBER_DOMAIN)
        ,'OFFLINE_IMG':settings.OFFLINE_IMG
    }
    if os.path.realpath(file).startswith(os.path.realpath(settings.STATIC_DIR)):
        data = open(file, 'r').read()
        data = data % context
        self.send_response(200)
        self.send_header("Content-type", 'text/html')
        self.send_header("Content-length", len(data))
        self.end_headers()
        self.wfile.write(data)
        
  def do_GET(self):
    isqs = self.path.find('?')    
    path = self.path
    if isqs > 0:
        path = path[:isqs]
    qs = self.path[self.path.find('?')+1:]
    qs = cgi.parse_qs(qs)
    
   # print path, qs
    #
    # /users?pwd=ADMIN_PASSWORD
    # /user/test@revolunet.com?pwd=ADMIN_PASSWORD
    # /user/test@revolunet.com?pwd=ADMIN_PASSWORD                           # return settings.ONLINE_IMG | OFFLINE_IMG
    # /send?jid=test@revolunet.com&msg=blalab%20balbal&pwd=ADMIN_PASSWORD
    #
    
    if qs.get('pwd',[''])[0] == settings.ADMIN_PASSWORD:
        if path == '/users':
            # list known users
            data = self.jabberCon.getStatus()
            return self.JsonResponse({'users':data})
        elif path == '/send':
            # send msg to specific user
            jid = qs.get('jid',[''])[0].lower()
            msg = qs.get('msg',[''])[0]
            self.jabberCon.sendMsg( jid, msg)
            return self.JsonResponse({'success':True})
    elif path.startswith('/user/'):
        # display user status
        paths = path[1:].split('/')
        jid = paths[-1].lower()
        data = self.jabberCon.getUserStatus(jid)
        return self.JsonResponse({'status':data})
    elif path.startswith('/status/'):
        # display user(s) status with an icon
        paths = path[1:].split('/')
        if len(paths) == 2:
            # specific user
            users = paths[-1].split(',')
            online = False
            for jid in users:
                #print "check", jid
                jid = jid.lower()
                if self.jabberCon.getUserStatus(jid) == 'online':
                    online = True
            if online == True:
                return self.ImgResponse( settings.ONLINE_IMG )
            else:
                return self.ImgResponse( settings.OFFLINE_IMG )
        else:
            self.JsonResponse({'success':False})
    elif path.startswith('/static/'):
        file = path[8:]
        file = file.replace('..', '')
        file = file.replace('/', '')
        file = file.replace('\\', '')
      #  print 'read ', file
        ext = file.lower()[file.rfind('.')+1:]
        if ext in 'jpg,jpeg,gif,png'.split(','):
                return self.ImgResponse( os.path.join(settings.STATIC_DIR, file) )
        elif ext in 'html,htm'.split(','):
                return self.HtmlResponse( os.path.join(settings.STATIC_DIR, file) )
    else:
        return self.HtmlResponse( os.path.join(settings.STATIC_DIR, 'home.html') )

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
