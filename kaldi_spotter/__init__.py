#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kaldi_spotter.settings import CONFIG
from kaldi_spotter.utils import play_sound, fuzzy_match
import logging
from nltools.pulserecorder import PulseRecorder
from nltools.vad import VAD, BUFFER_DURATION
from nltools.asr import ASR, ASR_ENGINE_NNET3
from pyee import EventEmitter
import json
from math import exp
from os.path import isfile


class KaldiWWSpotter(EventEmitter):
    def __init__(self, source=None, volume=None, aggressiveness=None,
                 model_dir=None, config=CONFIG):
        EventEmitter.__init__(self)
        self.config = config

        # ensure default values
        for k in CONFIG["listener"]:
            if k not in self.config["listener"]:
                self.config["listener"][k] = CONFIG["listener"][k]

        volume = volume or self.config["listener"]["default_volume"]
        aggressiveness = aggressiveness or self.config["listener"][
            "default_aggressiveness"]
        model_dir = model_dir or self.config["listener"]["default_model_dir"]

        self.rec = PulseRecorder(source_name=source, volume=volume)
        self.vad = VAD(aggressiveness=aggressiveness)
        logging.info("Loading model from %s ..." % model_dir)

        self.asr = ASR(engine=ASR_ENGINE_NNET3, model_dir=model_dir,
                       kaldi_beam=self.config["listener"]["default_beam"],
                       kaldi_acoustic_scale=self.config["listener"][
                           "default_acoustic_scale"],
                       kaldi_frame_subsampling_factor=self.config["listener"][
                           "default_frame_subsampling_factor"])
        self._hotwords = dict(self.config["hotwords"])

    def add_hotword(self, name, config=None):
        config = config or {"transcriptions": [name], "intent": name}
        self._hotwords[name] = config

    def remove_hotword(self, name):
        if name in self._hotwords.keys():
            self._hotwords.pop(name)

    @property
    def hotwords(self):
        return self._hotwords

    def _detection_event(self, message_type, message_data):
        serialized_message = json.dumps(
            {"type": message_type, "data": message_data})
        logging.debug(serialized_message)
        self.emit(message_type, serialized_message)

    def process_transcription(self, user_utt, confidence=0.99):
        for hotw in self.hotwords:
            if not self.hotwords[hotw].get("active"):
                continue
            rule = self.hotwords[hotw].get("rule", "sensitivity")
            s = 1 - self.hotwords[hotw].get("sensitivity", 0.2)
            confidence = (confidence + s) / 2
            for w in self.hotwords[hotw]["transcriptions"]:

                if (w in user_utt and rule == "in") or \
                        (user_utt.startswith(w) and rule == "start") or \
                        (user_utt.endswith(w) and rule == "end") or \
                        (fuzzy_match(w, user_utt) >= s and rule == "sensitivity") or \
                        (w == user_utt and rule == "equal"):
                    sound = self.hotwords[hotw].get("sound")
                    if sound and isfile(sound):
                        play_sound(sound)
                    self._detection_event("hotword",
                                          {"hotword": hotw,
                                           "utterance": user_utt,
                                           "confidence": confidence,
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
                self.process_transcription(user_utt, confidence)
