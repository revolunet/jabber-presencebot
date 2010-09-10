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



def remove_html_tags(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)
    
def remove_extra_spaces(data):
    p = re.compile(r'\s+')
    return p.sub(' ', data)
    
def html2plain(inHtml):
    inHtml = inHtml.replace('<br>', "\n")
    inHtml = inHtml.replace('<br/>', "\n")
    #print inHtml
    return remove_html_tags(inHtml)
    
class StatusBot(object):
    def __init__(self):
        self.client = xmpp.Client(settings.JABBER_DOMAIN, debug = settings.DEBUG) 
        self.client.connect( (settings.JABBER_HOST ,settings.JABBER_PORT) )
        self.client.auth(settings.JABBER_USER, settings.JABBER_PWD, 'python')
        self.client.sendInitPresence()
        self.client.RegisterHandler('presence', self.presenceHandler)
        self.client.RegisterDisconnectHandler( self.disconnectHandler )
        
    def disconnectHandler(self):
        print 'deconnected, reconnect'
        self.client.reconnectAndReauth()
        
    def getStatus(self, jids = []):
        # return a dict containing global status and detail on given jids
        data = {
            'online': False
            ,'details':{}
        }
   
        for jid in self.client.getRoster().getItems():
            if not jids or jid in jids:
                status = self.isAvailable(jid)
                data['details'][jid] = status
                if status:
                    data['online'] = True
                    
        for jid in jids:
            if not jid in data['details'].keys():
                data['details'][jid] = False
                
        return data
        
    def isAvailable(self, jid):
        # Bool
        # Return true if one jid online
        roster = self.client.getRoster()
        jids = jid.split(',')
        status = False
        for ajid in jids:
            show = roster.getShow(ajid)
            ress =  roster.getResources(ajid)
            if len(ress)> 0 and show in [None, 'online', 'available']:
                return True
        return False
        

    def sendMsg(self, jid, msg):
        # sends a jabber message (text+html)
        plain = html2plain(msg)
        message = xmpp.protocol.Message(jid, plain, 'chat')
        # if msg is HTML
        p_html = xmpp.Node("html",{"xmlns":'http://jabber.org/protocol/xhtml-im'})
        try:
            t1 = "<body xmlns='http://www.w3.org/1999/xhtml'>%s</body>" % msg
            html = xmpp.simplexml.XML2Node(t1)
            p_html.addChild(node=html)
            message.addChild(node=p_html)
        except:
            pass
        self.client.send(message)
        return True
        
         
   
        
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

  def JsonResponse(self, data, callback = None):
    response = json.dumps(data)
    ctype = 'application/json'
    if callback and callback != '':
        response = u"%s(%s);"  %( callback, response )
        ctype = 'text/javascript'
    self.send_response(200)
    self.send_header("Content-type", ctype)
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
        
  def HtmlResponse(self, file, ctype = 'text/html'):
    context = {
        'JABBER_USER':'%s@%s' % (settings.JABBER_USER, settings.JABBER_DOMAIN)
        ,'OFFLINE_IMG':settings.OFFLINE_IMG
    }
    if os.path.realpath(file).startswith(os.path.realpath(settings.STATIC_DIR)):
        data = open(file, 'r').read()
        data = data % context
        self.send_response(200)
        self.send_header("Content-type", ctype)
        self.send_header("Content-length", len(data))
        self.end_headers()
        self.wfile.write(data)
        
  def redirect(self, uri, code = 301):
        self.send_response( code )
        self.send_header("Location", uri)
        self.end_headers()
        
  def do_GET(self):
    isqs = self.path.find('?')    
    path = self.path
    if isqs > 0:
        path = path[:isqs]
    qs = self.path[self.path.find('?')+1:]
    qs = cgi.parse_qs(qs)
    
 
    if qs.get('pwd',[''])[0] == settings.ADMIN_PASSWORD:
        if path == '/users':
            # list known users
            data = self.jabberCon.getStatus()
            return self.JsonResponse({'users':data}, qs.get('callback',[''])[0])
        elif path == '/send':
            # send msg to specific user
            jid = qs.get('jid',[''])[0].lower()
            msg = qs.get('msg',[''])[0]
            self.jabberCon.sendMsg( jid, msg)
            return self.JsonResponse({'success':True}, qs.get('callback',[''])[0])
    elif path.startswith('/status/'):
        # JSON user(s) status
        paths = path[1:].split('/')
        jids = paths[-1].lower()
        data = self.jabberCon.getStatus( jids.split(',') )
        return self.JsonResponse({'status':data}, qs.get('callback',[''])[0])
    elif path.startswith('/imgstatus/'):
        # Image user(s) status
        paths = path[1:].split('/')
        jids = paths[-1].lower()
        data = self.jabberCon.getStatus( jids.split(',') )

        if data['online'] == True:
            if qs.get('on',[''])[0] !='':
                self.redirect(qs.get('on',[''])[0])
            else:
                return self.ImgResponse( settings.ONLINE_IMG )
        else:
            if qs.get('off',[''])[0] !='':
                self.redirect(qs.get('off',[''])[0])
            else:
                return self.ImgResponse( settings.OFFLINE_IMG )
                
    elif path.startswith('/static/'):
        # static files
        file = path[8:]
        file = file.replace('..', '')
        file = file.replace('/', '')
        file = file.replace('\\', '')
        ext = file.lower()[file.rfind('.')+1:]
        if ext in 'jpg,jpeg,gif,png'.split(','):
                return self.ImgResponse( os.path.join(settings.STATIC_DIR, file) )
        elif ext in 'html,htm'.split(','):
                return self.HtmlResponse( os.path.join(settings.STATIC_DIR, file) )
    elif path == '/widget.js':
        # special :/
        return self.HtmlResponse( os.path.join(settings.STATIC_DIR, 'widget.js') , ctype='text/javascript')
        
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
		if not hasattr(jabber.client, 'Process'):
			jabber = StatusBot()
			time.sleep(2)
			gateway = HTTPgateway(jabber)
			time.sleep(5)
        time.sleep(1)


if __name__ == '__main__':
    start()
