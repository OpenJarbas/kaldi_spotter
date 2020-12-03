class ModelNotFound(Exception):
    """ kaldi model not found """


class InvalidFileFormat(RuntimeError):
    """ Audio file must be WAV format mono PCM. """
