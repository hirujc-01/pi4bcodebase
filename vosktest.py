import sounddevice as sd
from vosk import Model, KaldiRecognizer
import numpy as np
import samplerate
import time
import json
import sys
import pyttsx3
import queue

engine = pyttsx3.init()
engine.setProperty('rate', 150)

TARGET_SR = 16000  # Vosk expects 16kHz audio
speech_queue = queue.Queue()

def get_default_input_samplerate():
    default_input_index = sd.default.device[0]
    if default_input_index is None or default_input_index < 0:
        devices = sd.query_devices()
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                default_input_index = i
                break
    device_info = sd.query_devices(default_input_index)
    return int(device_info['default_samplerate'])

def main():
    device_sr = get_default_input_samplerate()
    print(f"Device sample rate: {device_sr} Hz")
    print(f"Resampling audio to {TARGET_SR} Hz for Vosk")

    model = Model("../models/vosk-model-small-en-us-0.15")
    rec = KaldiRecognizer(model, TARGET_SR)

    need_resample = device_sr != TARGET_SR
    if need_resample:
        converter = samplerate.Resampler(converter_type='sinc_best')

    def callback(indata, frames, time_info, status):
        if status:
            print(status, file=sys.stderr)

        audio_data = np.frombuffer(indata, dtype=np.int16)

        if need_resample:
            audio_float = audio_data.astype(np.float32) / 32768.0
            audio_resampled = converter.process(audio_float, ratio=TARGET_SR / device_sr)
            audio_resampled_int16 = (audio_resampled * 32768).astype(np.int16)
            data_bytes = audio_resampled_int16.tobytes()
        else:
            data_bytes = indata

        if rec.AcceptWaveform(data_bytes):
            result = json.loads(rec.Result())
            text = result.get('text', '').lower()
            if text:
                speach_queue.put(f"You said: {text}")
                if "termination sequence initiate" in text:
                    speech_queue.put("Termination imminent")
                    speech_queue.put("__EXIT__")
                else:
                    speech_queue.put(f"You said: {text}")

    with sd.RawInputStream(samplerate=device_sr, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("Listening (say 'termination sequence initiate' to stop)...")
        while True:
            time.sleep(0.1)
            try:
                to_speak = speech_queue.get_nowait()
                if to_speak == "__EXIT__":
                    engine.say("Goodbye.")
                    engine.runAndWait()
                    break
                engine.say(to_speak)
                engine.runAndWait()
            except queue.Empty:
                continue

if __name__ == "__main__":
    main()
