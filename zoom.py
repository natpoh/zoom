import pyautogui as pg

import os
import datetime
import schedule
import time
import pyaudiowpatch as pyaudio
import audio_devices as ad
import subprocess
import csv
import random
import pygetwindow as gw

try:
    from config import conf_id, conf_pass, kirtan_folder
except ImportError:
    print("[INFO] Файл config.py не найден. Создаю config.py из шаблона config.py.example...")
    if os.path.exists("config.py.example"):
        import shutil
        shutil.copy("config.py.example", "config.py")
    else:
        with open("config.py", "w", encoding="utf-8") as f:
            f.write("# Данные для входа в Zoom\nconf_id = '85244706153'\nconf_pass = 'd3piUExIRlBaTkttZlRZM2xidGtlZz09'\n\n# Настройки\nkirtan_folder = 'C:/kirtans/'\n")
    from config import conf_id, conf_pass, kirtan_folder

def locate_image(image_path, **kwargs):
    full_path = os.path.join('images', image_path)
    if not os.path.exists(full_path):
        return None
    try:
        return pg.locateCenterOnScreen(full_path, **kwargs)
    except Exception:
        return None

global lastday
lastday = 0

# --- Звук: слушаем динамик, в который играет Zoom (WASAPI loopback) ---
ad.fix_console()
p = pyaudio.PyAudio()
CHUNK = 1024
silent_threshold = 10
time_wait = 60
try:
    from config import audio_output_device
except ImportError:
    audio_output_device = ''  # не выбран = системный динамик («Как в системе»)


def get_audio_stream(p_instance, speaker_name, chunk_val):
    speaker = ad.find_speaker(p_instance, speaker_name)
    if speaker_name and speaker is None:
        print(f"[WARNING] Динамик «{speaker_name}» из config.py не найден. Запустите setup.bat и выберите заново.")
    if speaker is not None:
        try:
            cap = ad.open_speaker_capture(p_instance, speaker, chunk_val)
            print(f"[INFO] Слушаю динамик: {speaker['name']} ({cap.rate} Гц, {cap.channels} кан.)")
            return cap, speaker
        except Exception as e:
            print(f"[WARNING] Не удалось открыть динамик «{speaker['name']}»: {e}")
    print("[INFO] Слушаю системный динамик (как в системе)...")
    speaker, cap = ad.open_default_speaker_capture(p_instance, chunk_val)
    print(f"[INFO] Слушаю динамик: {speaker['name']} ({cap.rate} Гц, {cap.channels} кан.)")
    return cap, speaker


capture, device = get_audio_stream(p, audio_output_device, CHUNK)
zoomfolder = 'zoommtg://zoom.us/join?action=join&confno=' + str(conf_id) + '&pwd=' + str(conf_pass)



def logfile(data):
    log_d = open("log.txt", "a")
    log_d.write(str(datetime.datetime.now()) + ' ' + str(data) + '\n')
    log_d.close()



def zoomcount():
    zoomcount = 0
    p_tasklist = subprocess.Popen('tasklist.exe /fo csv',
                                  stdout=subprocess.PIPE,
                                  universal_newlines=True)

    for row in csv.reader(p_tasklist.stdout):
        if row and row[0] == 'Zoom.exe':
            zoomcount = zoomcount + 1

    return zoomcount

def isWindowsProcessRunning( exeName ) :

    process = subprocess.Popen(
        'tasklist.exe /FO CSV /FI "IMAGENAME eq %s"' % exeName,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True )
    out, err = process.communicate()
    try : return out.split("\n")[1].startswith('"%s"' % exeName)
    except : return False



def zoomcounted():
    zoomcount = 0

    p_tasklist = subprocess.Popen('tasklist.exe /fo csv',
                                  stdout=subprocess.PIPE,
                                  universal_newlines=True)

    pythons_tasklist = []
    for row in csv.reader(p_tasklist.stdout):
        if row and row[0] == 'Zoom.exe':
            zoomcount = zoomcount + 1
            if len(row) > 1:
                pythons_tasklist.append(row[1])

    return pythons_tasklist

def savedata(zoomdata):
    os.makedirs('data', exist_ok=True)
    f = open('data/zoomdata.txt', 'w')
    f.write(str(zoomdata))
    f.close()
def checkzoom():
    zoomcount = zoomcounted()
    zoomcount.sort()
    zoomcount= str(zoomcount)
    print(zoomcount)

    os.makedirs('data', exist_ok=True)
    if not os.path.exists('data/zoomdata.txt'):
        savedata(zoomcount)

    zoomdata = ''
    f = open('data/zoomdata.txt', 'r')
    for line in f:
        zoomdata = line
        time.sleep(0.1)
    f.close()

    if zoomdata != zoomcount:
            print('похоже что зум закрыт '+zoomdata+' != '+zoomcount)
            rs = runzoom()
            if rs == 1:
                if zoomcount == '[]':
                    zoomcount = zoomcounted()
                    zoomcount.sort()
                    zoomcount = str(zoomcount)
                savedata(zoomcount)
                enable_sound()
                return 1
    else:
            print('ok '+zoomdata+' = '+zoomcount)



def check_users_sound(time_wait):
    if (runzoom()):
        for x in range(time_wait):
            # Пиковая громкость динамика за секунду (0 = тишина или Zoom ничего не играет).
            threshold = capture.wait_peak(1.0)
            if threshold > silent_threshold:
                print("Sound found at index " + str(x) + ': ' + str(threshold))

                pause_kirtan()
                return 1
            print(str(x) + ': ' + str(threshold))

        print("Sound is off. Play_kirtan" )
        logfile("Sound is off. Play_kirtan" )
        play_kirtan()
        return 0




def enable_sound():
        datapon = locate_image('poniatno.png', grayscale=True)
        if datapon:
            print('нажимаем понятно')
            pg.moveTo(datapon[0] + 5, datapon[1] + 5)
            pg.click()
            time.sleep(2)


        data = locate_image('mic_disabled.png',grayscale=True)
        if data:
            print('пытаемся включить звук')
            pg.moveTo(data[0] + 5, data[1] + 5)
            pg.click()
            time.sleep(2)




def is_zoom_meeting_active():
    try:
        titles = gw.getAllTitles()
        for title in titles:
            if 'Конференция' in title or 'Meeting' in title or title == 'Zoom':
                windows = gw.getWindowsWithTitle(title)
                if windows:
                    win = windows[0]
                    if win.isMinimized:
                        print(f'[DEBUG] Окно "{title}" свернуто. Разворачиваем...')
                        win.restore()
                return True
    except Exception as e:
        print(f'[DEBUG] Ошибка работы с окнами: {e}')
    return False

def runzoom():
    print('[DEBUG] Проверка окон Zoom...')
    if is_zoom_meeting_active():
        print('[DEBUG] Zoom-конференция активна.')
        return 1
    else:
        print('[DEBUG] Окно конференции не найдено. Запускаю Zoom по ссылке...')
        os.startfile(r'' + zoomfolder)
        print('[DEBUG] Жду 15 секунд пока загрузится Zoom...')
        time.sleep(15)
        return runzoom()


def getlastday(update):
    global lastday
    #print(lastday)
    if ((lastday == 0 ) or ( update == 1 ) ):
        if os.path.exists('lastday.txt'):
            f = open('lastday.txt', 'r')
            for lastday in f:
                 print('берем дату из файла '+str(lastday))
            f.close()
        else:
            lastday = 0


    now = datetime.datetime.now()
    d_date = now.timestamp()

    d_hour = now.hour
    d_minutes =now.minute

    dt_object = datetime.datetime.fromtimestamp(float(lastday))
    #print(dt_object)
    dt_hour = dt_object.hour
    dt_minutes =dt_object.minute

    #print(str(d_date)+' '+str(d_hour)+' '+str(d_minutes)+' ')
    #print(str(lastday)+' '+str(dt_hour)+' '+str(dt_minutes)+' ')

    #print(d_date)
    #

    if ( (int(d_hour) == int(dt_hour) and int(d_minutes) >= 30 and int(dt_minutes) < 30) or (int(d_hour) != int(dt_hour)) ):
        print(str(d_hour) +':'+str(d_minutes) +' > '+ str(dt_hour) +':'+str(dt_minutes) )
        if (update == 1):
            f = open('lastday.txt', 'w')
            f.write(str(d_date))

        lastday = d_date
        result = 1
    else:
        print(str(d_hour) + ':' + str(d_minutes) + ' < ' + str(dt_hour) + ':' + str(dt_minutes))
        result = 0
    

    return result
    
    
    
    
def pause_kirtan():
    #print('надо нажать на паузу')
    #print('проверяем может киртан уже играет')
    data = isWindowsProcessRunning('LA.exe')
    if data:
        os.system("TASKKILL /F /IM LA.exe")



def play_kirtan():
    print('проверяем может киртан уже играет')
    data = isWindowsProcessRunning('LA.exe')
    if data:
        print('плеер уже отктрыт')
        return 1

    print('проверяем включен ли звук')
    enable_sound()

    print('похоже что плеер закрыт пытаемся открыть')
    kirtan_name = check_last_played()
    
    logfile('запускаем файл ' + str(kirtan_name))
    print('запускаем файл ' + str(kirtan_name))
    os.startfile(r''+kirtan_folder+str(kirtan_name))


    return 1


        

def check_last_played():
    #проверяем какой киртан играл вчер

    lastsong = 0

    lastsong = 0
    if os.path.exists('list.txt'):
        try:
            f = open('list.txt', 'r')
            for line in f:
                lastsong = line.strip()
                print(lastsong)
            f.close()
        except Exception:
            lastsong = 0

    # берем список файлов
    directory = kirtan_folder
    if not os.path.exists(directory):
        print(f"[WARNING] Папка с аудио не найдена: {directory}")
        return lastsong
    files = os.listdir(directory)
    files = list(filter(lambda x: x.endswith('.mp3'), files))
    if not files:
        print(f"[WARNING] В папке {directory} нет .mp3 файлов!")
        return lastsong
    next_song = random.choice(files)

    index = 0
    # if lastsong!=0:
    #
    #     try:
    #         index = files.index(lastsong)
    #     except:
    #         index = 0
        
    #проверяем день тот же что и вчера или изменился
        
    day = getlastday(1)
    
    
    if (day==0):
        return lastsong

    
    #next_index = int(index)+1
    
    # try:
    #     next_song = files[next_index]
    # except:
    #     next_index = 0
    #     next_song = files[0]
    
    logfile(next_song)
    print(next_song)
    f = open('list.txt', 'w')
    f.write(next_song)
    f.close()
    return next_song
    


# schedule.every().day.at("00:00").do(pause_kirtan)

#проверяем включен ли звук каждые 100 секунд




logfile("script started")
if (runzoom()):
   enable_sound()

i = 0;
while True:
   i = i + 1
   played = check_users_sound(time_wait)
   #print (played)
   if played == 0:
       if (getlastday(0)):
           
           pause_kirtan()
           
       
    
   if played == 1 and i >= 10:
        print(i)
        enable_sound()
        i = 0
       
   time.sleep(1)


   
        
        
        
        