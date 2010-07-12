jabber-presencebot
==================

A simple Python/Jabber BOT that tracks online user presence.

Users add the bot to their roster and their status are then tracked.

The bot offers an http/json interface to query user statuses. results are JSON or images.

There is a working bot here : [http://status.revolunet.com][2]

**admin commands :** 

*theses commands need the pwd GET parameter (set in config)*

  - /users :    return the full roster with user status as json
  - /send?msg=blabla%20blabla&jid=aaa@gmail.com :  send a jabber message to aaa@gmail.com

**public commands :**

  - /user/aaa@gmail.com : return user aaa@gmail.com status as json
  - /status/aaa@gmail.com : return user aaa@gmail.com status as an image
  - /status/aaa@gmail.com,bbb@gmail.com,ccc@gmail.com :  return 'online' status image if one of these users or more is online.
  
  - the 'status' command can have 2 more params : on and off which are the online and offline image which will be displayed instead of the default.


**dependencies :** 

 * [xmpppy][1] 
 * python-simplejson
 

**authors**

 * Julien Bouquillon (revolunet) julien@bouquillon.com


  [1]: http://xmpppy.sourceforge.net/
  [2]: http://status.revolunet.com