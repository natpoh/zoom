import pyaudio
import os
import re
import sys
import io

if sys.platform == 'win32':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

def select_device():
    p = pyaudio.PyAudio()
    devices = []

    print("\n==========================================")
    print("   Список доступных устройств ввода аудио:")
    print("==========================================")

    for i in range(p.get_device_count()):
        try:
            info = p.get_device_info_by_index(i)
            if info.get('maxInputChannels', 0) > 0:
                name = info.get('name', 'Unknown')
                devices.append((i, name))
                print(f"  [{i}] {name}")
        except Exception:
            pass

    p.terminate()

    if not devices:
        print("[-] Устройства ввода аудио не обнаружены.")
        return

    print("==========================================")
    try:
        choice = input("Введите номер устройства для прослушки (или Enter для автопоиска): ").strip()
    except Exception:
        choice = ""

    if choice.isdigit():
        idx = int(choice)
        valid_indices = [d[0] for d in devices]
        if idx in valid_indices:
            config_file = 'config.py'
            if not os.path.exists(config_file):
                if os.path.exists('config.py.example'):
                    import shutil
                    shutil.copy('config.py.example', config_file)
                else:
                    with open(config_file, 'w', encoding='utf-8') as f:
                        f.write("# Config\nconf_id = '85244706153'\nconf_pass = 'd3piUExIRlBaTkttZlRZM2xidGtlZz09'\nkirtan_folder = 'C:/kirtans/'\n")

            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if 'audio_device_index' in content:
                content = re.sub(r'audio_device_index\s*=\s*\d+', f'audio_device_index = {idx}', content)
            else:
                content += f'\naudio_device_index = {idx}\n'

            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(content)

            selected_name = next(name for i_dev, name in devices if i_dev == idx)
            print(f"\n[УСПЕХ] Выбрано устройство #{idx} ({selected_name}).")
            print(f"Настройка сохранена в config.py.")
        else:
            print("\n[ВНИМАНИЕ] Указан неверный номер. Оставлен автопоиск.")
    else:
        print("\n[ИНФО] Оставлен автоматический выбор устройства.")

if __name__ == "__main__":
    select_device()
