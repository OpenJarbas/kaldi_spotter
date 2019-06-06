from os.path import isfile, expanduser
from kaldi_spotter.utils import load_commented_json, merge_dict

CONFIG = {
    "listener": {
        "default_volume": 150,
        "default_aggressiveness": 2,
        "default_model_dir": '/opt/kaldi/model/kaldi-generic-en-tdnn_250',
        "default_acoustic_scale": 1.0,
        "default_beam": 7.0,
        "default_frame_subsampling_factor": 3,
    },
    "hotwords": {}
}

_paths = [
    "/opt/kaldi_spotter/kaldi_spotter.conf",
    expanduser("~/.kaldi_spotter/kaldi_spotter.conf")
]

for p in _paths:
    if isfile(p):
        merge_dict(CONFIG, load_commented_json(p))




