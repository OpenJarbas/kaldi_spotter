#!/usr/bin/env python
# -*- coding: utf-8 -*-
from kaldi_spotter.utils import play_sound, fuzzy_match
from kaldi_spotter.exceptions import ModelNotFound, InvalidFileFormat
import logging
from json_database import JsonStorage
from vosk import Model as KaldiModel, KaldiRecognizer
from pyee import EventEmitter
import json
from os.path import isdir, isfile
import pyaudio
from kaldi_spotter.vad import vad_collector


class KaldiWWSpotter(EventEmitter):
    def __init__(self, config):
        super().__init__()
        if isinstance(config, dict):
            self.config = config
        elif isinstance(config, str):
            self.config = JsonStorage(config)

        model = self.config.get("model_folder")
        if not model or not isdir(model):
            raise ModelNotFound

        listener_config = self.config.get("listener") or \
                          {"vad_agressiveness": 2,
                           "sample_rate": 16000,
                           "start_thresh": 1,
                           "end_thresh": 3}
        self.vad_agressiveness = listener_config["vad_agressiveness"]
        self.sample_rate = listener_config["sample_rate"]
        self.start_thresh = listener_config["start_thresh"]
        self.end_thresh = listener_config["end_thresh"]

        self.model = KaldiModel(model)
        self.kaldi = KaldiRecognizer(self.model, self.sample_rate)
        self._hotwords = dict(self.config.get("hotwords", {}))

        self.running = False
        self.speaking = False
        self.result = None

    def add_hotword(self, name, config=None):
        config = config or {"transcriptions": [name], "intent": name}
        self._hotwords[name] = config

    def remove_hotword(self, name):
        if name in self._hotwords.keys():
            self._hotwords.pop(name)

    @property
    def hotwords(self):
        return self._hotwords

    def emit_detection_event(self, message_type, message_data=None):
        message_data = message_data or self.result
        serialized_message = json.dumps(message_data)
        logging.debug(serialized_message)
        self.emit(message_type, serialized_message)

    def _process_transcription(self):
        user_utt = self.result.get("text")

        for hotw in self.hotwords:
            if not self.hotwords[hotw].get("active"):
                continue
            rule = self.hotwords[hotw].get("rule", "sensitivity")
            s = 1 - self.hotwords[hotw].get("sensitivity", 0.2)
            confidence = (self.confidence + s) / 2

            for w in self.hotwords[hotw]["transcriptions"]:
                found = False

                if w in user_utt and rule == "in":
                    found = True
                elif user_utt.startswith(w) and rule == "start":
                    found = True
                elif user_utt.endswith(w) and rule == "end":
                    found = True
                elif w == user_utt and rule == "equal":
                    found = True
                elif rule == "sensitivity" and fuzzy_match(w, user_utt) >= s:
                    found = True

                if found:
                    yield {"hotword": hotw,
                           "utterance": user_utt,
                           "confidence": confidence,
                           "intent": self.hotwords[hotw]["intent"]}

    def _hotword_events(self):
        for hw_data in self._process_transcription():
            sound = self.hotwords[hw_data["hotword"]].get("sound")
            if sound and isfile(sound):
                play_sound(sound)
            self.emit_detection_event("hotword", hw_data)

    def feed_chunk(self, chunk):
        if self.kaldi.AcceptWaveform(chunk):
            self.result = json.loads(self.kaldi.Result())
        else:
            transcript_data = json.loads(self.kaldi.PartialResult())
            if transcript_data != self.result:
                self.result = transcript_data
                if transcript_data["partial"]:
                    self.emit_detection_event("transcription.partial")

    def finalize(self):
        final = json.loads(self.kaldi.FinalResult())
        if final["text"]:
            self.result = final
        if self.result.get("text"):
            self.emit_detection_event("transcription")
            self._hotword_events()
        else:
            self.emit_detection_event("transcription.failure",
                                      {"error": "empty text transcription"})
        data = dict(self.result)
        self.result = {}
        self.speaking = False
        return data

    @property
    def confidence(self):
        try:
            return sum([w["conf"] for w in self.result["result"]]) / len(
                self.result["result"])
        except:
            return 0

    def run(self):

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                        input=True, frames_per_buffer=8000)
        stream.start_stream()
        logging.info("Listening")

        counter = 0
        silence_counter = 0

        prev_chunk = None
        self.running = True
        while self.running:
            data = stream.read(4000)
            if len(data) == 0:
                continue
            is_speaking = vad_collector(data, self.sample_rate,
                                        self.vad_agressiveness)
            if is_speaking:
                counter += 1
                silence_counter = 0
                if counter >= self.start_thresh and not self.speaking:
                    self.speaking = True
                    event_data = {"thresh": self.start_thresh,
                                  "agressiveness": self.vad_agressiveness}
                    self.emit_detection_event("vad.start", event_data)
                    self.feed_chunk(prev_chunk)
                if self.speaking:
                    self.feed_chunk(data)
            else:
                if self.speaking and silence_counter >= self.end_thresh:
                    event_data = {"timesteps": counter,
                                  "agressiveness": self.vad_agressiveness}
                    self.emit_detection_event("vad.end", event_data)
                    self.finalize()

                silence_counter += 1
                counter = 0
            prev_chunk = data

    def stop(self):
        # TODO close pyaudio stream
        self.running = False
