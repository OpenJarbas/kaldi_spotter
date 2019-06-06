# Kaldi Spotter

wake word spotting with kaldi

- [Kaldi Spotter](#kaldi-spotter)
  * [Usage](#usage)
    + [Config](#config)
      - [Sample Config](#sample-config)
    + [Code](#code)
    + [Sample Output](#sample-output)
  * [Install](#install)
    + [Raspbian 9 (stretch) on a Raspberry Pi 2/3](#raspbian-9--stretch--on-a-raspberry-pi-2-3)
    + [Debian 9 (stretch, amd64)](#debian-9--stretch--amd64-)
    + [CentOS 7 (amd64)](#centos-7--amd64-)
  * [TODO](#todo)
  * [Credits](#credits)

  
## Usage

### Config

Configuration is loaded from the following locations, with each location 
overriding values from the previous one

    "/opt/kaldi_spotter/kaldi_spotter.conf"
    "~/.kaldi_spotter/kaldi_spotter.conf"
    
#### Sample Config

```json5
{
    # kaldi config
    "listener": {
        "default_volume": 150,
        "default_aggressiveness": 2,
        "default_model_dir": '/opt/kaldi/model/kaldi-generic-en-tdnn_250',
        "default_acoustic_scale": 1.0,
        "default_beam": 7.0,
        "default_frame_subsampling_factor": 3,
    },
    "hotwords": {
        # simple commands
        "hello": {
            "transcriptions": ["hello"],
            "sound": None,
            "intent": "greeting",
            "active": True,

            # in - anywhere in utterance (default)
            # start - start of utterance
            # end - end of utterance
            # equal - exact match
            "rule": "start"
        },
        "thank you": {
            "transcriptions": ["thank you"],
            "sound": None,
            "intent": "thank",
            "active": True
        },
        # full sentences
        # CRITERIA
        # - fairly accurate,
        # - important enough to want offline functionality
        # - worth answering even if speech not directed at device
        "lights on": {
            "transcriptions": ["lights on"],
            "sound": None,
            "intent": "turn on lights",
            "active": True,
            "rule": "equal"
        },
        "lights off": {
            "transcriptions": ["lights off"],
            "sound": None,
            "intent": "turn off lights",
            "active": True,
            "rule": "equal"
        },
        "time": {
            "transcriptions": ["what time is it"],
            "sound": None,
            "intent": "current time",
            "active": True,
            "rule": "equal"
        },
        "weather": {
            "transcriptions": ["what's the weather like",
                               "what's the weather life",
                               "what is the weather like",
                               "what is the weather life",
                               "what the weather like"],
            "sound": None,
            "intent": "weather forecast",
            "active": True,
            "rule": "equal"
        },

        # wake words
        # PROTIP: just run the live demo and see which transcriptions come up
        "christopher": {
            "transcriptions": ["christopher"],
            "sound": None,
            "intent": "listen",
            "active": True
        },
        "hey marty": {
            "transcriptions": ["hey marty"],
            "sound": None,
            "intent": "listen",
            "active": True
        },
        "hey mycroft": {
            # not in language model
            "transcriptions": ["hey mike off", "hey microsoft",
                               "hey migrants"],
            "sound": None,
            "intent": "listen",
            "active": True
        },
        "hey robin": {
            # seems to struggle with this one
            "transcriptions": ["hey rob him", "hey rob in", "hey robin",
                               "hey rob it", "hey rob", "a robin"],
            "sound": None,
            "intent": "listen",
            "active": True
        },
        "hey mike": {
            "transcriptions": ["hey mike"],
            "sound": None,
            "intent": "listen",
            "active": True
        },
        "hey joe": {
            "transcriptions": ["hey joe"],
            "sound": None,
            "intent": "listen",
            "active": True
        },
        "hey johnnie": {
            "transcriptions": ["hey johnnie"],
            "sound": None,
            "intent": "listen",
            "active": True
        },
        "hey jonathan": {
            "transcriptions": ["hey jonathan"],
            "sound": None,
            "intent": "listen",
            "active": True
        },
        "hey bob": {
            "transcriptions": ["hey bob"],
            "sound": None,
            "intent": "listen",
            "active": True
        },
        "hey lex": {
            "transcriptions": ["hey lex"],
            "sound": None,
            "intent": "listen",
            "active": True
        },
        "hey computer": {
            "transcriptions": ["hey computer", "a computer", "they computer"],
            "sound": None,
            "intent": "listen",
            "active": True
        }
    }
}
```

### Code

see [examples](./examples)

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
('LIVE TRANSCRIPTION:', '{"data": {"confidence": 0.7698909431952632, "utterance": "hey computer"}, "type": "transcription"}')
('HOTWORD:', '{"data": {"hotword": "hey computer", "utterance": "hey computer", "intent": "listen"}, "type": "hotword"}')
('LIVE TRANSCRIPTION:', '{"data": {"confidence": 0.7663563699360755, "utterance": "what time is it"}, "type": "transcription"}')
('HOTWORD:', '{"data": {"hotword": "time", "utterance": "what time is it", "intent": "what time is it"}, "type": "hotword"}')

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

- allow passing config in constructor
- setup.py + pip package

## Credits

[zamia-speech](https://github.com/gooofy/zamia-speech)