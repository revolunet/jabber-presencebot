revolunet statusbot
===================

A simple Python/Jabber BOT that tracks online user presence.

Users add the bot to their roster and their status are then tracked.

The bot offers an http/json interface to query user statuses. results are JSON or images

 * AUTHENTICATED COMMANDS : 
 
/users                                              return the full roster with user status (online/offlince)
/send?msg=blabla%20blabla&jid=aaa@gmail.com         send jabber message to aaa@gmail.com

 * ANONYMOUS COMMANDS : 

/user/aaa@gmail.com                                   return user aaa@gmail.com status (online/offline)
/status/aaa@gmail.com                                 return user aaa@gmail.com status (online/offline) as an image
/status/aaa@gmail.com,bbb@gmail.com,ccc@gmail.com     return 'online' status if any of these users is online

all the commands must use GET and pwd passed

dependencies : xmpppy http://xmpppy.sourceforge.net/