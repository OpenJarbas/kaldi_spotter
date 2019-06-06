from kaldi_spotter import KaldiWWSpotter

CONFIG = {
    "lang": "en",  # "en" or "de" pre-trained models available
    "listener": {
        "default_volume": 150,
        "default_aggressiveness": 2,
        "default_model_dir": '/opt/kaldi/model/kaldi-generic-{lang}-tdnn_250',
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
            # in - anywhere in utterance
            # start - start of utterance
            # end - end of utterance
            # equal - exact match
            # sensitivity - fuzzy match and score transcription (error tolerant) <- default
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
            "sensitivity": 0.2,
            # if score > 1 - sensitivity -> detection
            # hey computer * a computer == 0.8181818181818182
            # "hey mycroft" * "hey microsoft" == 0.8333333333333334
            "rule": "sensitivity"
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


def print_hotword(event):
    print("HOTWORD:", event)


def print_utterance(event):
    print("LIVE TRANSCRIPTION:", event)


listener = KaldiWWSpotter(config=CONFIG)
listener.on("transcription", print_utterance)
listener.on("hotword", print_hotword)
listener.run()
