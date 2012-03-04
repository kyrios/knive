#name = string(min=1, max=30, default=Fred)
#age = float(min=0, max=200, default=29)
#attributes = string_list(min=5, max=5, default=list('arms', 'legs', 'head', 'body', 'others'))
#likes_cheese = boolean(default=True)
#favourite_color = option('red', 'green', 'blue', default="red")

[paths]
ffmpegbin = string(default=/usr/bin/ffmpeg)

[logging]
logfile = string(default=./knive.log)
loglevel = option('DEBUG', 'INFO', 'WARN')
filesize = integer(min=1,max=65000,default=256)
keepfiles = integer(min=0,max=1000,default=3)

[webservice]
enabled=boolean(default=False)
port=integer(min=1024,max=65000,default=8000)

[channels]
    [[__many__]]
    name=string(min=3,max=30)
    slug=string(min=3,max=30)
    url=string(min=3,max=100,default='http://example.com')

    [[[outlets]]]
        [[[[__many__]]]]
        type=option('HTTPLive','FileArchiver')
        publishURL=string
        outputLocation=string
            [[[[[__many__]]]]]
            vcodec=string(default=None)
            acodec=string(default=None)
            crf=integer(default=None)
            g=integer(default=None)
            b=string(default=None)
            vn=boolean(default=None)

    [[[source]]]
    type=option('kniveTCPSource', 'kniveFileSource', 'kniveIcecastSource')
    listenAddress=string(default='0.0.0.0')
    listenPort=integer(default=3333)
    sharedSecret=string(min=5)



# outlet=string(min=3,max=30)
# episodes=string_list
# 
#     [[__many__]]
#     type=option('distributor', 'httplive', 'filewriter')
        
