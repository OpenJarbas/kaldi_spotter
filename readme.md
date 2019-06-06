# Kaldi Spotter

wake word spotting with kaldi

- [Kaldi Spotter](#kaldi-spotter)
  * [Usage](#usage)
    + [Sample Output](#sample-output)
  * [Install](#install)
    + [Raspbian 9 (stretch) on a Raspberry Pi 2/3](#raspbian-9--stretch--on-a-raspberry-pi-2-3)
    + [Debian 9 (stretch, amd64)](#debian-9--stretch--amd64-)
    + [CentOS 7 (amd64)](#centos-7--amd64-)
  * [TODO](#todo)
  * [Credits](#credits)
  
## Usage

edit CONFIG in kaldi_spotter.py

```python
from kaldi_spotter import KaldiWWSpotter
    
def print_hotword(event):
    print("HOTWORD:", event)


def print_utterance(event):
    print("LIVE TRANSCRIPTION:", event)


listener = KaldiWWSpotter()
listener.on("transcription", print_utterance)
listener.on("hotword", print_hotword)
listener.run()
``` 

### Sample Output

```bash
pi@raspberrypi:~ $ python kaldi_spotter.py 
INFO:root:Loading model from /opt/kaldi/model/kaldi-generic-en-tdnn_250 ...
INFO:root:audio source: seeed-4mic-voicecard Multichannel
INFO:root:Listening
('LIVE TRANSCRIPTION:', '{"data": {"confidence": 1.2445470094680786, "utterance": "hey computer"}, "type": "transcription"}')
('HOTWORD:', '{"data": {"hotword": "hey computer", "intent": "listen", "utterance": "hey computer"}, "type": "hotword"}')
('LIVE TRANSCRIPTION:', '{"data": {"confidence": 1.3947328329086304, "utterance": "what time is it"}, "type": "transcription"}')
('HOTWORD:', '{"data": {"hotword": "time", "intent": "current time", "utterance": "what time is it"}, "type": "hotword"}')

```

## Install

### Raspbian 9 (stretch) on a Raspberry Pi 2/3
```bash
echo "deb http://goofy.zamia.org/repo-ai/raspbian/stretch/armhf/ ./" >/etc/apt/sources.list.d/zamia-ai.list
wget -qO - http://goofy.zamia.org/repo-ai/raspbian/stretch/armhf/bofh.asc | sudo apt-key add -
apt-get update
apt-get install kaldi-chain-zamia-speech-de kaldi-chain-zamia-speech-en python-kaldiasr python-nltools pulseaudio-utils pulseaudio
pip install pyee
```

### Debian 9 (stretch, amd64)
```bash
apt-get install apt-transport-https
echo "deb http://goofy.zamia.org/repo-ai/debian/stretch/amd64/ ./" >/etc/apt/sources.list.d/zamia-ai.list
wget -qO - http://goofy.zamia.org/repo-ai/debian/stretch/amd64/bofh.asc | sudo apt-key add -
apt-get update
apt-get install kaldi-chain-zamia-speech-de kaldi-chain-zamia-speech-en python-kaldiasr python-nltools pulseaudio-utils pulseaudio
pip install pyee
```


### CentOS 7 (amd64)
```bash
cd /etc/yum.repos.d
wget http://goofy.zamia.org/zamia-speech/misc/zamia-ai-centos.repo
yum install kaldi-chain-zamia-speech-de kaldi-chain-zamia-speech-en python-kaldiasr python-nltools pulseaudio-utils pulseaudio
pip install pyee
```

## TODO

- read config from file
- play sound util (on detection) or deprecate that field in config
- setup.py + pip package

## Credits

[zamia-speech](https://github.com/gooofy/zamia-speech)