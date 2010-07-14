
var statusWidget_host = 'http://status.revolunet.com';

function loadScript(url, callback){

    var script = document.createElement("script")
    script.type = "text/javascript";

    if (script.readyState){  //IE
        script.onreadystatechange = function(){
            if (script.readyState == "loaded" ||
                    script.readyState == "complete"){
                script.onreadystatechange = null;
                callback();
            }
        };
    } else {  //Others
        script.onload = function(){
            callback();
        };
    }

    script.src = url;
    document.getElementsByTagName("head")[0].appendChild(script);
}



var statusWidget = {
    config:null
    ,loaded:false
    ,req:null
    ,status:'offline'
    ,init:function() {
        if (!document.readyState == 'complete') {
            setTimeout(statusWidget.init, 250);
            return;
        }
        this.loaded = true;
        // config
        this.config = {
            target:null
            ,onImage:statusWidget_host + '/static/live-chat-button-online.gif'
            ,offImage:statusWidget_host + '/static/live-chat-button-offline.gif'
            ,hideIfOffline:false
            ,jids:[]
            ,offUrl:null
            ,onUrl:null
        }
        if (typeof(statusWidget_config) == 'object') {
            for (a in statusWidget_config) {
                this.config[a] = statusWidget_config[a]
                //console.log(a, eDemo_config[a]);
            }
        }
 
       this.initStatus( );

    }
    ,receiveStatus:function(json) {
        if (json.status.online === true) {
            this.status = 'online';
            this.onOnline();
        }
        else {
            this.status = 'offline';
            this.onOffline();
        }
        
    }
    ,onOnline:function() {
        this.setImage( this.config.onImage );
        var tgt = document.getElementById('statusWidget_img');
        if (tgt) tgt.style.display = 'block';
    }
    ,onOffline:function() {
        this.setImage( this.config.offImage );
        document.getElementById('statusWidget_img').style.display = (this.config.hideIfOffline) ?  'none':'block';
        
    }
    ,initStatus:function() {
            var url = statusWidget_host + '/status/' + statusWidget.config.jids.join(',');
            url += "?callback=statusWidget.receiveStatus&r=" + Math.random();
            loadScript(url, function () {/* callback */ });
            setTimeout(statusWidget.initStatus, 10000);
             
    }
    
    ,onImageClick:function() {
       if (this.status == 'online' && this.config.onUrl) {
            document.location = this.config.onUrl;
            }
       else if (this.config.offUrl) {
        document.location = this.config.offUrl;
       }
    }
    ,setImage:function( url ) {
            if (this.config.target) {
                var tgt = document.getElementById(this.config.target);
                //alert(tgt);
                }
            else {
                var tgt = document.getElementById('statusWidget');
                if (!tgt) {
                    var div = document.createElement('DIV');
                    div.setAttribute('id', 'statusWidget');
                    document.body.appendChild( div );
                    tgt = document.getElementById('statusWidget');
          
                }
                }
            if (tgt) {
                tgt.innerHTML = "<img  id='statusWidget_img', src='" + url  + "' style='cursor:pointer' onclick='statusWidget.onImageClick();' />";
            }
    
    
    }

    
}
statusWidget.init();


/*
INSERT THIS IN YOUR PAGE

<!-- START statusWidget WIDGET --> 
<script type="text/javascript"> 

// OPTIONAL CONFIG PARAMS
// var statusWidget_config = {
//      target:'divId'
//      ,onImage:'/path/to/online.png'
//      ,offImage:'/path/to/offline.png'
//      ,hideIfOffline:false
//      ,jids:['jid@gmail.com', 'jid@revolunet.com']    // query using these JID 
//      ,onUrl:'http://chat-page.html'
//      ,offUrl:'http://contact-page.html'
// }

</script> 
<script type="text/javascript" src="http://status.revolunet.com/widget.js"></script>

<!-- END statusWidget WIDGET -->

*/  