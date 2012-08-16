Simple installation
===================
./configure && make
make install


Verbose Installation
====================
Below you find the general installation notes. For OS specific notes see further below.

OS independent notes
--------------------

### Prerequisites
* libavformat >= 52.92.0
* libavcodec
* libavutil
* [twisted >= 10.2.0](http://www.twistedmatrix.com)

### required Python Libraries:
* pycrpto (For manhole service)
* pyasn1 (For manhole service)

Hint:
	sudo easy_install pycrypto pyasn1



OS-X Installation Notes
-----------------------
These notes where written using Mac OS-X Moutain Lion (10.8)
You will need to have Xcode (or at least the commandline tools) and homebrew installed for these instructions to apply.

* Install [XQuartz](http://xquartz.macosforge.org/landing/) - Required for ffmpeg formula
* Install FFMpeg
	brew install ffmpeg

./configure
make
sudo make install
