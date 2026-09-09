# -*- coding: utf-8 -*-
"""Просто показать все динамики, которые видит бот."""
import pyaudiowpatch as pyaudio
import audio_devices as ad

ad.fix_console()
p = pyaudio.PyAudio()
for s in ad.list_speakers(p):
    print(f"[{s['index']:3d}] {s['name']}  {s['rate']} Гц, {s['channels']} кан." + ("  <- системный" if s['default'] else ''))
p.terminate()
