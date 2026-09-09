# -*- coding: utf-8 -*-
"""Показать живую громкость динамика, выбранного в config.py (Ctrl+C = выход)."""
import sys
import pyaudiowpatch as pyaudio
import audio_devices as ad

ad.fix_console()
try:
    from config import audio_output_device
except ImportError:
    audio_output_device = ''

p = pyaudio.PyAudio()
speaker = ad.find_speaker(p, audio_output_device)
if speaker is None:
    speaker, cap = ad.open_default_speaker_capture(p)
else:
    cap = ad.open_speaker_capture(p, speaker)
print(f"Слушаю: {speaker['name']}  ({cap.rate} Гц, {cap.channels} кан.)")
try:
    while True:
        v = cap.wait_peak(0.2)
        sys.stdout.write(f"\r[{ad.level_bar(v)}] {v:5d}   ")
        sys.stdout.flush()
except KeyboardInterrupt:
    pass
finally:
    cap.close()
    p.terminate()
