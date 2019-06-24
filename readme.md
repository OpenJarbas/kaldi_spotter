# Kaldi Spotter

wake word spotting with kaldi

- [Kaldi Spotter](#kaldi-spotter)
  * [Usage](#usage)
    + [Config](#config)
      - [Sample Config](#sample-config)
    + [Python](#python)
    + [CLI](#cli)
    + [Sample Output](#sample-output)
  * [Install](#install)
    + [System Requirements](#system-requirements)
    + [Pre-trained models](#pre-trained-models)
      - [Raspbian 9 (stretch) on a Raspberry Pi 2/3](#raspbian-9--stretch--on-a-raspberry-pi-2-3)
      - [Debian 9 (stretch, amd64)](#debian-9--stretch--amd64-)
      - [CentOS 7 (amd64)](#centos-7--amd64-)
    + [Pip Package](#pip-package)
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
    "listener": {
        "default_volume": 150,
        "default_aggressiveness": 2,
        "default_model_dir": "/opt/kaldi/model/kaldi-generic-en-tdnn_250",
        "default_acoustic_scale": 1.0,
        "default_beam": 7.0,
        "default_frame_subsampling_factor": 3
    },
    "hotwords": {
        # full sentences
        # CRITERIA
        # - fairly accurate,
        # - important enough to want offline functionality
        # - worth answering even if speech not directed at device
        "lights on": {
            "transcriptions": ["lights on"],
            "intent": "turn on lights",
            "rule": "equal"
        },
        "lights off": {
            "transcriptions": ["lights off"],
            "intent": "turn off lights",
            "rule": "equal"
        },
        "time": {
            "transcriptions": ["what time is it"],
            "intent": "current time",
            "active": false,
            "rule": "equal"
        },
        # wake words
        # PROTIP: just run the live demo and see which transcriptions come up
        "hey computer": {
            "transcriptions": ["hey computer", "a computer", "they computer"],
            "sound": "/home/pi/start_listening.wav",
            "intent": "listen"
        }
    }
}
```

### Python

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

### CLI

Start kaldi spotter from cli

```bash
python -m kaldi_spotter
```

### Sample Output

```bash
pi@raspberrypi:~ $ python -m kaldi_spotter
INFO:root:Loading model from /opt/kaldi/model/kaldi-generic-en-tdnn_250 ...
INFO:root:audio source: seeed-4mic-voicecard Multichannel
INFO:root:Listening
('LIVE TRANSCRIPTION:', '{"data": {"confidence": 0.7698909431952632, "utterance": "hey computer"}, "type": "transcription"}')
('HOTWORD:', '{"data": {"hotword": "hey computer", "utterance": "hey computer", "intent": "listen"}, "type": "hotword"}')
('LIVE TRANSCRIPTION:', '{"data": {"confidence": 0.7663563699360755, "utterance": "what time is it"}, "type": "transcription"}')
('HOTWORD:', '{"data": {"hotword": "time", "utterance": "what time is it", "intent": "current time"}, "type": "hotword"}')

```

## Install

### System Requirements

```bash
sudo apt-get install libatlas-dev pulseaudio-utils pulseaudio cython
```

### Pre-trained models

You can install English model ```kaldi-chain-zamia-speech-en``` or german model ```kaldi-chain-zamia-speech-de```

Refered as ```kaldi-chain-zamia-speech-XX``` bellow

#### Raspbian 9 (stretch) on a Raspberry Pi 2/3
```bash
echo "deb http://goofy.zamia.org/repo-ai/raspbian/stretch/armhf/ ./" >/etc/apt/sources.list.d/zamia-ai.list
wget -qO - http://goofy.zamia.org/repo-ai/raspbian/stretch/armhf/bofh.asc | sudo apt-key add -
apt-get update
apt-get install kaldi-chain-zamia-speech-XX
```

#### Debian 9 (stretch, amd64)
```bash
apt-get install apt-transport-https
echo "deb http://goofy.zamia.org/repo-ai/debian/stretch/amd64/ ./" >/etc/apt/sources.list.d/zamia-ai.list
wget -qO - http://goofy.zamia.org/repo-ai/debian/stretch/amd64/bofh.asc | sudo apt-key add -
apt-get update
apt-get install kaldi-chain-zamia-speech-XX
```

#### CentOS 7 (amd64)
```bash
cd /etc/yum.repos.d
wget http://goofy.zamia.org/zamia-speech/misc/zamia-ai-centos.repo
yum install kaldi-chain-zamia-speech-XX
```

### Pip Package

install from pip

```bash
pip install kaldi_spotter
```

or from source

```bash
pip install git+https://github.com/JarbasAl/kaldi_spotter
```

## Credits

[zamia-speech](https://github.com/gooofy/zamia-speech)
