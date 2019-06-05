#!/usr/bin/env python
# -*- coding: utf-8 -*- 

DEFAULT_VOLUME = 150
DEFAULT_AGGRESSIVENESS = 2
DEFAULT_MODEL_DIR = '/opt/kaldi/model/kaldi-generic-en-tdnn_250'
DEFAULT_ACOUSTIC_SCALE = 1.0
DEFAULT_BEAM = 7.0
DEFAULT_FRAME_SUBSAMPLING_FACTOR = 3

# listening config
CONFIG = {

    # need to match transcription
    "commands": {
        # full sentences
        # CRITERIA
        # - fairly accurate,
        # - important enough to want offline functionality
        # - worth answering even if speech not directed at device
        "lights on": {
            "transcriptions": ["lights on"],
            "sound": None,
            "intent": "turn on lights",
            "active": True
        },
        "lights off": {
            "transcriptions": ["lights off"],
            "sound": None,
            "intent": "turn off lights",
            "active": True
        },
        "time": {
            "transcriptions": ["what time is it"],
            "sound": None,
            "intent": "what time is it",
            "active": True
        },
        "weather": {
            "transcriptions": ["what's the weather like",
                               "what's the weather life"],
            "sound": None,
            "intent": "turn off lights",
            "active": True
        }

    },

    # need to be present in transcription
    "hotwords": {
        # simple commands
        "hello": {
            "transcriptions": ["hello"],
            "sound": None,
            "intent": "greeting",
            "active": True
        },
        "thank you": {
            "transcriptions": ["thank you"],
            "sound": None,
            "intent": "thank",
            "active": True
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
from nltools import misc
from nltools.pulserecorder import PulseRecorder
from nltools.vad import VAD, BUFFER_DURATION
from nltools.asr import ASR, ASR_ENGINE_NNET3
from optparse import OptionParser

from pyee import EventEmitter
import json


class LocalListener(EventEmitter):
    hotwords = CONFIG["hotwords"]
    commands = CONFIG["commands"]

    def initialize(self, source , volume, aggressiveness, model_dir):
        self.rec = PulseRecorder(source_name=source, volume=volume)
        self.vad = VAD(aggressiveness=aggressiveness)
        logging.info("Loading model from %s ..." % model_dir)

        self.asr = ASR(engine=ASR_ENGINE_NNET3, model_dir=model_dir,
                       kaldi_beam=DEFAULT_BEAM,
                       kaldi_acoustic_scale=DEFAULT_ACOUSTIC_SCALE,
                       kaldi_frame_subsampling_factor=DEFAULT_FRAME_SUBSAMPLING_FACTOR)

    def _emit(self, message_type, message_data):
        serialized_message = json.dumps(
            {"type": message_type, "data": message_data})
        logging.debug(serialized_message)
        # TODO plug into mycroft message bus
        self.emit(serialized_message)

    def on_transcription(self, user_utt, confidence):
        for cmd in self.commands:
            if not self.commands[cmd].get("active"):
                continue
            for c in self.commands[cmd]["transcriptions"]:
                if c.lower().strip() == user_utt.lower().strip():
                    data = self.commands[cmd]
                    data["confidence"] = confidence
                    data["command"] = cmd
                    self._emit("command", data)
                    return
        for hotw in self.hotwords:
            if not self.hotwords[hotw].get("active"):
                continue
            for w in self.hotwords[hotw]["transcriptions"]:
                if w in user_utt:
                    data = self.hotwords[hotw]
                    data["confidence"] = confidence
                    data["hotword"] = hotw
                    self._emit("hotword", data)
                    return

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
                                                   stream_id=STREAM_ID)

            if finalize:
                self.on_transcription(user_utt, confidence)


if __name__ == "__main__":
    PROC_TITLE = 'kaldi_live'

    STREAM_ID = 'mic'

    misc.init_app(PROC_TITLE)

    parser = OptionParser("usage: %prog [options]")

    parser.add_option("-a", "--aggressiveness", dest="aggressiveness", type="int",
                      default=DEFAULT_AGGRESSIVENESS,
                      help="VAD aggressiveness, default: %d" % DEFAULT_AGGRESSIVENESS)

    parser.add_option("-m", "--model-dir", dest="model_dir", type="string",
                      default=DEFAULT_MODEL_DIR,
                      help="kaldi model directory, default: %s" % DEFAULT_MODEL_DIR)

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="verbose output")

    parser.add_option("-s", "--source", dest="source", type="string", default=None,
                      help="pulseaudio source, default: auto-detect mic")

    parser.add_option("-V", "--volume", dest="volume", type="int",
                      default=DEFAULT_VOLUME,
                      help="broker port, default: %d" % DEFAULT_VOLUME)

    (options, args) = parser.parse_args()

    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    source = options.source
    volume = options.volume
    aggressiveness = options.aggressiveness
    model_dir = options.model_dir

    listener = LocalListener()
    listener.initialize(source, volume, aggressiveness, model_dir)
    listener.run()
