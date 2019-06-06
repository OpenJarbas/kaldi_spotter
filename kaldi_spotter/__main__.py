from optparse import OptionParser
import logging

from kaldi_spotter.settings import CONFIG
from kaldi_spotter import KaldiWWSpotter

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
