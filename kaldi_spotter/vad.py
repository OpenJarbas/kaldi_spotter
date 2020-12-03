import webrtcvad
import pyaudio


class Frame:
    """Represents a "frame" of audio data."""

    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    """Generates audio frames from PCM audio data.
    Takes the desired frame duration in milliseconds, the PCM data, and
    the sample rate.
    Yields Frames of the requested duration.
    """
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(audio, sample_rate=16000, agressiveness=1):
    """Filters out non-voiced audio frames.
    Given a webrtcvad.Vad and a source of audio frames, yields only
    the voiced audio.
    Uses a padded, sliding window algorithm over the audio frames.
    When more than 90% of the frames in the window are voiced (as
    reported by the VAD), the collector triggers and begins yielding
    audio frames. Then the collector waits until 90% of the frames in
    the window are unvoiced to detrigger.
    The window is padded at the front and back to provide a small
    amount of silence or the beginnings/endings of speech around the
    voiced frames.
    Arguments:
    sample_rate - The audio sample rate, in Hz.
    frame_duration_ms - The frame duration in milliseconds.
    padding_duration_ms - The amount to pad the window, in milliseconds.
    vad - An instance of webrtcvad.Vad.
    frames - a source of audio frames (sequence or generator).
    Returns: A generator that yields PCM audio data.
    """
    vad = webrtcvad.Vad(agressiveness)
    frames = frame_generator(30, audio, sample_rate)
    frames = list(frames)

    total = len(frames)
    detections = 0
    for frame in frames:
        is_speech = vad.is_speech(frame.bytes, sample_rate)
        if is_speech:
            detections += 1
    if detections >= total / 2:
        return True
    return False


if __name__ == '__main__':
    sample_rate = 16000
    agressiveness = 1

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=sample_rate,
                    input=True, frames_per_buffer=8000)
    stream.start_stream()
    print("Listening")

    counter = 0
    thresh = 2
    speaking = False
    while True:
        audio = stream.read(4000)
        is_speaking = vad_collector(audio, sample_rate, agressiveness)
        if is_speaking:
            counter += 1
            if counter >= thresh and not speaking:
                print("Speech started")
                speaking = True
        else:

            if speaking:
                print("Speak finished")
                speaking = False
                print("timesteps", counter)
            counter = 0
