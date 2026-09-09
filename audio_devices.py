# -*- coding: utf-8 -*-
"""Работа со звуком: список динамиков (устройств воспроизведения) и захват того,
что в них играет (WASAPI loopback). Используется и в setup (select_audio.py), и в zoom.py."""
import re
import sys
import io
import threading
import time
from array import array

import pyaudiowpatch as pyaudio


def fix_console():
    """Чтобы русские названия устройств не превращались в кракозябры в консоли."""
    if sys.platform == 'win32':
        for name in ('stdout', 'stderr'):
            try:
                setattr(sys, name, io.TextIOWrapper(getattr(sys, name).buffer, encoding='utf-8', errors='replace'))
            except Exception:
                pass


def list_speakers(p):
    """Все динамики (устройства воспроизведения) по WASAPI.
    Возвращает список словарей: index, name, default (True = 'как в системе'), rate, channels."""
    api = p.get_host_api_info_by_type(pyaudio.paWASAPI)
    default_index = api.get('defaultOutputDevice', -1)
    speakers = []
    for i in range(p.get_device_count()):
        try:
            d = p.get_device_info_by_index(i)
        except Exception:
            continue
        if d.get('hostApi') != api['index']:
            continue
        if d.get('maxOutputChannels', 0) <= 0 or d.get('isLoopbackDevice'):
            continue
        speakers.append({
            'index': i,
            'name': d['name'],
            'default': i == default_index,
            'rate': int(d.get('defaultSampleRate', 48000)),
            'channels': int(d.get('maxOutputChannels', 2)),
        })
    # Системный динамик всегда первым, остальные по алфавиту.
    speakers.sort(key=lambda s: (not s['default'], s['name'].lower()))
    return speakers


def _key(name):
    return re.sub(r'\s+', ' ', name).strip().lower()


def find_speaker(p, name):
    """Динамик по имени (имя храним в config.py: индексы меняются после перезагрузки)."""
    if not name:
        return None
    speakers = list_speakers(p)
    for s in speakers:
        if s['name'] == name:
            return s
    for s in speakers:
        if _key(s['name']) == _key(name):
            return s
    return None


def loopback_for(p, speaker):
    """Устройство-'подслушка' (loopback) для данного динамика."""
    for lb in p.get_loopback_device_info_generator():
        if lb.get('isLoopbackDevice') and lb['name'].startswith(speaker['name']):
            return lb
    return None


class SpeakerCapture:
    """Подслушка динамика. Ловушка WASAPI loopback: пока в динамик ничего не играет,
    устройство не отдаёт НИ ОДНОГО куска, и обычный stream.read() виснет навсегда.
    Поэтому читаем через callback, а «данных нет» считаем тишиной (громкость 0)."""

    def __init__(self, p, speaker, chunk=1024):
        lb = loopback_for(p, speaker)
        if lb is None:
            raise RuntimeError("Не нашёл loopback для динамика: " + speaker['name'])
        self.speaker = speaker
        self.rate = int(lb.get('defaultSampleRate', speaker['rate']))
        self.channels = int(lb.get('maxInputChannels', 2)) or 2
        self.loopback = lb['name']
        self._lock = threading.Lock()
        self._cond = threading.Condition(self._lock)
        self._peak = 0          # максимум с момента последнего take()
        self._chunks = 0        # сколько кусков пришло всего
        self._stream = p.open(format=pyaudio.paInt16, channels=self.channels, rate=self.rate, input=True,
                              frames_per_buffer=chunk, input_device_index=lb['index'],
                              stream_callback=self._on_data)
        self._stream.start_stream()

    def _on_data(self, in_data, frame_count, time_info, status):
        v = peak(in_data)
        with self._cond:
            self._peak = max(self._peak, v)
            self._chunks += 1
            self._cond.notify_all()
        return (None, pyaudio.paContinue)

    def wait_peak(self, seconds):
        """Пиковая громкость за следующие `seconds` секунд. 0, если динамик молчал (или спал)."""
        end = time.time() + seconds
        with self._cond:
            self._peak = 0
            while True:
                left = end - time.time()
                if left <= 0:
                    break
                self._cond.wait(left)
            return self._peak

    def close(self):
        try:
            self._stream.stop_stream()
            self._stream.close()
        except Exception:
            pass


def open_speaker_capture(p, speaker, chunk=1024):
    """Открывает подслушку выбранного динамика."""
    return SpeakerCapture(p, speaker, chunk)


def open_default_speaker_capture(p, chunk=1024):
    """Если динамик в config.py не выбран, слушаем системный ('как в системе' в Zoom)."""
    speakers = list_speakers(p)
    if not speakers:
        raise RuntimeError("В системе нет ни одного устройства воспроизведения (WASAPI)")
    s = speakers[0]  # системный отсортирован первым
    return s, SpeakerCapture(p, s, chunk)


def peak(data):
    """Пиковая громкость куска 16-битного звука (0..32767). Замена audioop.max: его нет в Python 3.13+."""
    samples = array('h')
    samples.frombytes(data[: len(data) - (len(data) % 2)])
    if not samples:
        return 0
    return max(abs(x) for x in samples)


def level_bar(value, width=40, full=8000):
    n = min(width, int(value / full * width))
    return '#' * n + '.' * (width - n)
