# knive.conf.spec
# Copyright (c) 2012 Thorsten Philipp <kyrios@kyri0s.de>

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#name = string(min=1, max=30, default=Fred)
#age = float(min=0, max=200, default=29)
#attributes = string_list(min=5, max=5, default=list('arms', 'legs', 'head', 'body', 'others'))
#likes_cheese = boolean(default=True)
#favourite_color = option('red', 'green', 'blue', default="red")

[paths]
ffmpegbin = string(default=/usr/bin/ffmpeg)
segmenterbin = string(default=/usr/local/bin/live_segmenter)
knivedata = string(default=/var/www/knive)

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
    url=string(min=3,max=100,default='http://example.com')

    [[[outlets]]]
        [[[[__many__]]]]
        type=option('HTTPLive','FileArchiver')
        publishURL=string
        outputLocation=string(default='httplive')
            [[[[[__many__]]]]]
            vcodec=string(default=None)
            acodec=string(default=None)
            crf=integer(default=None)
            g=integer(default=None)
            b=string(default=None)
            vn=boolean(default=None)
            f=string(default=mpegts)

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
        
