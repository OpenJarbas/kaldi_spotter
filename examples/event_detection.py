from kaldi_spotter import KaldiWWSpotter
import json


def parse_event(event):
    while isinstance(event, str):
        event = json.loads(event)
    return event


def print_hotword(event):
    event = parse_event(event)
    print("HOTWORD:", event)


def print_partial_utterance(event):
    event = parse_event(event)
    print("PARTIAL TRANSCRIPTION:", event)


def print_utterance(event):
    event = parse_event(event)
    print("LIVE TRANSCRIPTION:", event)


def print_utterance_fail(event):
    event = parse_event(event)
    print("TRANSCRIPTION FAILURE", event)


def print_start(event):
    event = parse_event(event)
    print("SPEECH STARTED", event)


def print_end(event):
    event = parse_event(event)
    print("SPEECH ENDED", event)


config = {
    "model_folder": "/home/user/Downloads/vosk-model-small-en-us-0.4"
}
listener = KaldiWWSpotter(config)
listener.on("vad.start", print_start)
listener.on("vad.end", print_end)
listener.on("transcription.partial", print_partial_utterance)
listener.on("transcription", print_utterance)
listener.on("hotword", print_hotword)

listener.run()
