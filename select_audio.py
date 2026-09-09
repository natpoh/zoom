# -*- coding: utf-8 -*-
"""Шаг установки: выбрать динамик, который Zoom использует для воспроизведения.
Бот подслушивает этот динамик, чтобы понять, говорит ли кто-то в конференции."""
import os
import re
import shutil
import sys
import time

import pyaudiowpatch as pyaudio

import audio_devices as ad

ad.fix_console()

CONFIG = 'config.py'
LINE = '=' * 60


def ensure_config():
    if os.path.exists(CONFIG):
        return
    if os.path.exists('config.py.example'):
        shutil.copy('config.py.example', CONFIG)
    else:
        with open(CONFIG, 'w', encoding='utf-8') as f:
            f.write("# Данные для входа в Zoom\nconf_id = ''\nconf_pass = ''\n\nkirtan_folder = 'C:/kirtans/'\n")


def save_choice(name):
    """name = '' означает системный динамик («Как в системе»)."""
    ensure_config()
    with open(CONFIG, 'r', encoding='utf-8') as f:
        content = f.read()
    value = repr(name)
    if re.search(r'^audio_output_device\s*=', content, re.M):
        content = re.sub(r'^audio_output_device\s*=.*$', 'audio_output_device = ' + value, content, flags=re.M)
    else:
        content = content.rstrip('\n') + (
            "\n\n# Динамик, который выбран в Zoom -> Звук -> «Выберите динамик».\n"
            "# Пустая строка = системный динамик («Как в системе»). Переизбрать: setup.bat\n"
            "audio_output_device = " + value + "\n")
    # Старая настройка (номер микрофона) больше не используется.
    content = re.sub(r'^audio_device_index\s*=.*\n?', '', content, flags=re.M)
    with open(CONFIG, 'w', encoding='utf-8') as f:
        f.write(content)


def listen_test(p, speaker, seconds=8):
    print()
    print(f"Проверка: {seconds} сек. слушаю динамик «{speaker['name']}».")
    print("Включите любой звук на этом динамике (YouTube, музыку, или пусть кто-то говорит в Zoom).")
    try:
        cap = ad.open_speaker_capture(p, speaker)
    except Exception as e:
        print(f"[ОШИБКА] Не удалось открыть динамик: {e}")
        return False
    heard = 0
    end = time.time() + seconds
    try:
        while time.time() < end:
            v = cap.wait_peak(0.2)
            heard = max(heard, v)
            sys.stdout.write(f"\r  громкость [{ad.level_bar(v)}] {v:5d}   ")
            sys.stdout.flush()
    finally:
        cap.close()
    print()
    if heard > 10:
        print(f"[OK] Звук слышен (пик {heard}). Бот будет слушать этот динамик.")
    else:
        print("[ВНИМАНИЕ] За время проверки звука не было. Это нормально, если ничего не играло.")
        print("           Если играло, то в Zoom выбран другой динамик. Запустите setup.bat ещё раз.")
    return True


def select_device():
    p = pyaudio.PyAudio()
    try:
        speakers = ad.list_speakers(p)
        print()
        print(LINE)
        print("   Какой динамик слушать?")
        print(LINE)
        print("Откройте Zoom -> стрелка рядом с кнопкой «Звук» -> раздел «Выберите динамик».")
        print("Выберите здесь ТОТ ЖЕ пункт, что отмечен галочкой в Zoom.")
        print("Если в Zoom отмечено «Как в системе», выбирайте пункт [1].")
        print()
        if not speakers:
            print("[-] Устройств воспроизведения не найдено.")
            return
        for n, s in enumerate(speakers, 1):
            mark = '   <- как в системе (по умолчанию)' if s['default'] else ''
            print(f"  [{n}] {s['name']}{mark}")
        print()
        try:
            choice = input(f"Номер динамика (1-{len(speakers)}, Enter = [1]): ").strip()
        except Exception:
            choice = ''
        if choice == '':
            chosen = speakers[0]
        elif choice.isdigit() and 1 <= int(choice) <= len(speakers):
            chosen = speakers[int(choice) - 1]
        else:
            print("\n[ВНИМАНИЕ] Неверный номер. Оставлен системный динамик.")
            chosen = speakers[0]
        save_choice('' if chosen['default'] else chosen['name'])
        print(f"\n[СОХРАНЕНО] Бот будет слушать: {chosen['name']}  (записано в config.py)")
        listen_test(p, chosen)
    finally:
        p.terminate()


if __name__ == '__main__':
    select_device()
