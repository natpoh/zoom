import pyaudio
p = pyaudio.PyAudio()
for device in range(p.get_device_count()):
    info = p.get_device_info_by_index(device)
    if info['maxInputChannels'] > 0:
        for rate in [44100, 48000]:
            for channels in [1, 2]:
                try:
                    stream = p.open(format=pyaudio.paInt16, channels=channels, rate=rate, input=True, frames_per_buffer=1024, input_device_index=device)
                    print(f"SUCCESS: Device {device} ({info['name']}) with {channels} channels at {rate} Hz")
                    stream.close()
                except Exception:
                    pass

