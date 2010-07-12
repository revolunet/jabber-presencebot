revolunet statusbot
===================

A simple Python/Jabber BOT that tracks online user presence.

Users add the bot to their roster and their status are then tracked.

The bot offers an http/json interface to query user statuses. results are JSON. 

/users                                              return the full roster with user status (online/offlince)
/user/aaa@gmail.com                                 return user aaa@gmail.com status (online/offline)
/send?msg=blabla%20blabla&jid=aaa@gmail.com         send jabber message to aaa@gmail.com


all the commands must use GET and pwd passed

dependencies : xmpppy http://xmpppy.sourceforge.net/