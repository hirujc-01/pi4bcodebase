import sounddevice as sd
from vosk import Model, KaldiRecognizer
import sys
import numpy as np
import samplerate  # pip install samplerate
import time

TARGET_SR = 16000  # Vosk expects 16kHz audio

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

    model = Model("models/vosk-model-en-us-0.15")
    rec = KaldiRecognizer(model, TARGET_SR)

    # Prepare resampler if needed
    need_resample = device_sr != TARGET_SR
    if need_resample:
        converter = samplerate.Resampler(converter_type='sinc_best')  # high quality resampler

    def callback(indata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        # indata is bytes or numpy array of int16
        audio_data = np.frombuffer(indata, dtype=np.int16)

        if need_resample:
            # Convert int16 to float32 for resampling, range [-1, 1]
            audio_float = audio_data.astype(np.float32) / 32768.0
            audio_resampled = converter.process(audio_float, ratio=TARGET_SR / device_sr)
            # Convert back to int16
            audio_resampled_int16 = (audio_resampled * 32768).astype(np.int16)
            data_bytes = audio_resampled_int16.tobytes()
        else:
            data_bytes = indata

        if rec.AcceptWaveform(data_bytes):
            print(rec.Result())
        else:
            print(rec.PartialResult())

    with sd.RawInputStream(samplerate=device_sr, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print("Listening (Ctrl+C to stop)...")
        while True:
            time.sleep(0.1)

if __name__ == "__main__":
    main()
