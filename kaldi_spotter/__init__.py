#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kaldi_spotter.settings import CONFIG
from kaldi_spotter.utils import play_sound
import logging
from nltools.pulserecorder import PulseRecorder
from nltools.vad import VAD, BUFFER_DURATION
from nltools.asr import ASR, ASR_ENGINE_NNET3
from optparse import OptionParser
from pyee import EventEmitter
import json
from math import exp
from os.path import isfile


class KaldiWWSpotter(EventEmitter):
    def __init__(self,
                   source=None,
                   volume=CONFIG["listener"]["default_volume"],
                   aggressiveness=CONFIG["listener"]["default_aggressiveness"],
                   model_dir=CONFIG["listener"]["default_model_dir"]):
        EventEmitter.__init__(self)
        self.rec = PulseRecorder(source_name=source, volume=volume)
        self.vad = VAD(aggressiveness=aggressiveness)
        logging.info("Loading model from %s ..." % model_dir)

        self.asr = ASR(engine=ASR_ENGINE_NNET3, model_dir=model_dir,
                       kaldi_beam=CONFIG["listener"]["default_beam"],
                       kaldi_acoustic_scale=CONFIG["listener"][
                           "default_acoustic_scale"],
                       kaldi_frame_subsampling_factor=CONFIG["listener"][
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
                    sound = self.hotwords[hotw].get("sound")
                    if sound and isfile(sound):
                        play_sound(sound)
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
            confidence = 1 - exp(-1 * confidence)
            if finalize and user_utt:
                self._detection_event("transcription",
                                      {"utterance": user_utt,
                                       "confidence": confidence})
                self.process_transcription(user_utt)


if __name__ == "__main__":
    parser = OptionParser("usage: %prog [options]")

    parser.add_option("-a", "--aggressiveness", dest="aggressiveness",
                      type="int",
                      default=CONFIG["listener"]["default_aggressiveness"],
                      help="VAD aggressiveness, default: %d" %
                           CONFIG["listener"]["default_aggressiveness"])

    parser.add_option("-m", "--model-dir", dest="model_dir", type="string",
                      default=CONFIG["listener"]["default_model_dir"],
                      help="kaldi model directory, default: %s" %
                           CONFIG["listener"]["default_model_dir"])

    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="verbose output")

    parser.add_option("-s", "--source", dest="source", type="string",
                      default=None,
                      help="pulseaudio source, default: auto-detect mic")

    parser.add_option("-V", "--volume", dest="volume", type="int",
                      default=CONFIG["listener"]["default_volume"],
                      help="broker port, default: %d" % CONFIG["listener"][
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


    listener = KaldiWWSpotter(source, volume, aggressiveness, model_dir)
    listener.on("transcription", print_utterance)
    listener.on("hotword", print_hotword)

    listener.run()
