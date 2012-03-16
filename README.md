jabber-presencebot
==================

A simple Python/Jabber BOT that tracks online user presence.

Users add the bot to their roster and their status are then tracked.

The bot offers an http/json interface to query user statuses. results are JSON or images.

There is also a JS API to display your team jabber status and redirect users accordingly. 

You can also use client.py on remote servers to track their status (add this script to your @reboot cron command)


**usage :**

  - edit settings.py
  - python ./statusbot.py
  
  

**server admin commands :** 

*theses commands need the pwd GET parameter (set in config)*

  - /users :    return the full roster with user status as json
  - /send?msg=blabla%20blabla&jid=aaa@gmail.com :  send a jabber message to aaa@gmail.com

**public commands :**

  - /status/aaa@gmail.com : return user aaa@gmail.com status as json
  - /status/aaa@gmail.com,bbb@gmail.com,ccc@gmail.com :  return 'online' status as json
  - /imgstatus/aaa@gmail.com : display online image if this user online
  - /imgstatus/aaa@gmail.com,bbb@gmail.com : display online image if one of this user online
  
  - the 'imgstatus' command takes two optional params : on and off which are the online and offline image which will be displayed instead of the default.
  - Json commands have a 'callback' optional parameters that you can use to cross-domain include this result in your applications. (remote script include)
  

    
**dependencies :** 

 * [xmpppy][1] 
 * python-simplejson
 

**authors**

 * Julien Bouquillon (revolunet) julien@bouquillon.com


  [1]: http://xmpppy.sourceforge.net/
  [2]: http://status.revolunet.com