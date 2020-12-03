# Kaldi Spotter

wake word spotting with kaldi

- [Kaldi Spotter](#kaldi-spotter)
  * [Config](#config)
  * [Usage](#usage)
    + [Sample Output](#sample-output)
  * [Install](#install)
    + [Pre-trained models](#pre-trained-models)
  

## Config

```json5
{
    "listener": {
        "vad_agressiveness": 2,
        "sample_rate": 16000,
        "start_thresh": 1,
        "end_thresh": 3
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

## Usage


see [examples](./examples)

```python
from kaldi_spotter import KaldiWWSpotter
    
def print_hotword(event):
    print("HOTWORD:", event)


def print_utterance(event):
    print("LIVE TRANSCRIPTION:", event)

config = {"model_folder": "path_to_folder"}
listener = KaldiWWSpotter(config)
listener.on("transcription", print_utterance)
listener.on("hotword", print_hotword)
listener.run()
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

install from pip

```bash
pip install kaldi_spotter
```

or from source

```bash
pip install git+https://github.com/JarbasAl/kaldi_spotter
```

### Pre-trained models

You can download official models from [alphacephei](https://alphacephei.com/vosk/models)

Models for Iberian Languages can be found [here](https://github.com/JarbasIberianLanguageResources/iberian-vosk) 
