#!/usr/bin/env python
# -*- coding: utf-8 -*- 

# listening config
CONFIG = {
    # kaldi config
    "kaldi": {
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
                               "hey rob it", "hey rob"],
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

import logging
from nltools.pulserecorder import PulseRecorder
from nltools.vad import VAD, BUFFER_DURATION
from nltools.asr import ASR, ASR_ENGINE_NNET3
from optparse import OptionParser

from pyee import EventEmitter
import json


class KaldiWWSpotter(EventEmitter):
    def initialize(self,
                   source=None,
                   volume=CONFIG["kaldi"]["default_volume"],
                   aggressiveness=CONFIG["kaldi"]["default_aggressiveness"],
                   model_dir=CONFIG["kaldi"]["default_model_dir"]):

        self.rec = PulseRecorder(source_name=source, volume=volume)
        self.vad = VAD(aggressiveness=aggressiveness)
        logging.info("Loading model from %s ..." % model_dir)

        self.asr = ASR(engine=ASR_ENGINE_NNET3, model_dir=model_dir,
                       kaldi_beam=CONFIG["kaldi"]["default_beam"],
                       kaldi_acoustic_scale=CONFIG["kaldi"][
                           "default_acoustic_scale"],
                       kaldi_frame_subsampling_factor=CONFIG["kaldi"][
                           "default_frame_subsampling_factor"])
        self._hotwords = dict(CONFIG["hotwords"])

    def add_hotword(self, name, config=None):
        config = config or {"transcriptions": [name], "intent": name}
        self._hotwords[name] = config

    @property
    def hotwords(self):
        return self._hotwords

    def _detection_event(self, message_type, message_data):
        serialized_message = json.dumps(
            {"type": message_type, "data": message_data})
        logging.debug(serialized_message)
        self.emit(message_type, serialized_message)

    def process_transcription(self, user_utt):
        for hotw in self.hotwords:
            if not self.hotwords[hotw].get("active"):
                continue
            rule = self.hotwords[hotw].get("rule", "in")
            for w in self.hotwords[hotw]["transcriptions"]:
                if (w in user_utt and rule == "in") or \
                        (user_utt.startswith(w) and rule == "start") or \
                        (user_utt.endswith(w) and rule == "end") or \
                        (w == user_utt and rule == "equal"):
                    self._detection_event("hotword",
                                          {"hotword": hotw,
                                           "utterance": user_utt,
                                           "intent": self.hotwords[hotw]["intent"]})

    def run(self):

        self.rec.start_recording()
        logging.info("Listening")

        while True:

            samples = self.rec.get_samples()

            audio, finalize = self.vad.process_audio(samples)

            if not audio:
                continue

            logging.debug('decoding audio len=%d finalize=%s audio=%s' % (
                len(audio), repr(finalize), audio[0].__class__))

            user_utt, confidence = self.asr.decode(audio, finalize,
                                                   stream_id="mic")

            if finalize and user_utt:
                self._detection_event("transcription",
                                      {"utterance": user_utt,
                                       "confidence": confidence})
                self.process_transcription(user_utt)


if __name__ == "__main__":
    parser = OptionParser("usage: %prog [options]")

    parser.add_option("-a", "--aggressiveness", dest="aggressiveness",
                      type="int",
                      default=CONFIG["kaldi"]["default_aggressiveness"],
                      help="VAD aggressiveness, default: %d" %
                           CONFIG["kaldi"]["default_aggressiveness"])

    parser.add_option("-m", "--model-dir", dest="model_dir", type="string",
                      default=CONFIG["kaldi"]["default_model_dir"],
                      help="kaldi model directory, default: %s" %
                           CONFIG["kaldi"]["default_model_dir"])

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="verbose output")

    parser.add_option("-s", "--source", dest="source", type="string",
                      default=None,
                      help="pulseaudio source, default: auto-detect mic")

    parser.add_option("-V", "--volume", dest="volume", type="int",
                      default=CONFIG["kaldi"]["default_volume"],
                      help="broker port, default: %d" % CONFIG["kaldi"][
                          "default_volume"])

    (options, args) = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    source = options.source
    volume = options.volume
    aggressiveness = options.aggressiveness
    model_dir = options.model_dir


    def print_hotword(event):
        print("HOTWORD:", event)


    def print_utterance(event):
        print("LIVE TRANSCRIPTION:", event)


    listener = KaldiWWSpotter()
    listener.initialize(source, volume, aggressiveness, model_dir)
    listener.on("transcription", print_utterance)
    listener.on("hotword", print_hotword)

    listener.run()
