import pyautogui as pg

import os
import datetime
import schedule
import time
import pyaudio
import audioop
import subprocess
import csv
import random

from config import conf_id, conf_pass, kirtan_folder

def locate_image(image_path, **kwargs):
    if not os.path.exists(image_path):
        return None
    return locate_image(image_path, **kwargs)

global lastday
lastday = 0
p = pyaudio.PyAudio()
CHUNK = 1024
FORMAT = pyaudio.paInt16
RATE = 44100
silent_threshold = 10
time_wait = 60
device = 2

#conf_id = '8829424825'
#conf_id = '9264933287'
#conf_pass = 'bnk'
#time_wait = 6
#device = 1

zoomfolder ='zoommtg://zoom.us/join?action=join&confno='+str(conf_id)+'&pwd='+str(conf_pass)



channels=p.get_device_info_by_index(device)
print(channels)

stream = p.open(format=FORMAT, channels=p.get_device_info_by_index(device).get('maxInputChannels'), rate=RATE,
                input=True, frames_per_buffer=CHUNK, input_device_index=device)


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
    f = open('data/zoomdata.txt', 'w')
    f.write(str(zoomdata))
    f.close()
def checkzoom():
    zoomcount = zoomcounted()
    zoomcount.sort()
    zoomcount= str(zoomcount)
    print(zoomcount)

    f = open('data/zoomdata.txt', 'r')

    for zoomdata in f:
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
            data = stream.read(CHUNK)
            threshold = audioop.max(data, 2)
            #print(str(x) + ': ' + str(threshold))
            if threshold > silent_threshold:
                print("Sound found at index " + str(x) + ': ' + str(threshold))
                
                pause_kirtan()
                return 1
            print(str(x) + ': ' + str(threshold))
            time.sleep(1)

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

        dataorg = locate_image('org_enable_sound.png', grayscale=True)
        if dataorg:
            print('нажимаем включить звук от организатора')
            pg.moveTo(dataorg[0] + 5, dataorg[1] + 5)
            pg.click()
            time.sleep(2)


        data = locate_image('mic_disabled.png',grayscale=True)
        if data:
            print('пытаемся включить звук')
            pg.moveTo(data[0] + 5, data[1] + 5)
            pg.click()
            time.sleep(2)



        data = locate_image('original_sound.png',grayscale=True)
        if data:
            print('пытаемся включить оригинальный звук')
            pg.moveTo(data[0] + 5, data[1] + 5)
            pg.click()



def runzoom():
    count = zoomcount()
    print(f'[DEBUG] Проверка процессов Zoom... Найдено: {count}')
    
    if count >= 2:
        print('[DEBUG] Zoom запущен (найдено 2 или более процессов).')
        return 1
    else:
        print(f'[DEBUG] Zoom не открыт (нужно >=2 процессов, а есть {count}).')
        print(f'[DEBUG] Запускаю Zoom по ссылке...')
        os.startfile(r'' + zoomfolder)
        print('[DEBUG] Жду 15 секунд пока загрузится Zoom...')
        time.sleep(15)
        return runzoom()

    return

    data = locate_image('zoom_opened.png',grayscale=True)
    if data:
        return 1
    print('не вижу открытое окно зум')
    logfile("zoom closed")
    print('нажимаем кнопку ОК в окне зум')
    data = locate_image('ok.png')
    if data:
                    pg.moveTo(data[0] + 5, data[1] + 5)
                    print('нажимаем кнопку ОК в окне зум')
                    pg.click()
                    time.sleep(2)
                    
    data = locate_image('poniatno.png')
    if data:
                    pg.moveTo(data[0] + 5, data[1] + 5)
                    pg.click()
                    print('нажимаем кнопку понятно в окне зум') 
                    time.sleep(2)
        
    data = locate_image('fulscreen.png')
    if data:
        pg.moveTo(data[0] + 5, data[1] + 5)
        pg.click()
        time.sleep(2)
        print('разворачиваем свернутое окно')
        return runzoom()
 
    data = locate_image('fulscreen_2.png')
    if data:
        pg.moveTo(data[0] + 5, data[1] + 5)
        pg.click()
        time.sleep(2)
        print('разворачиваем свернутое окно')
        return runzoom()
    
    

        
        #проверяем может зум уже открыт
    print('проверяем может зум уже открыт')
    data = locate_image('disabled_login.png')
    if data:
            print('похоже зум уже открыт и свернут пытаемся развернуть')            
            data = locate_image('zoom_shotcout_big.png')
            if data:
                pg.moveTo(data[0] + 5, data[1] + 5)
                pg.click()
                time.sleep(1)
                pg.moveTo(data[0] +100, data[1] - 100)
                pg.click()
                time.sleep(1)
                print('нажали чтобы открыть зум')
                time.sleep(2)

           

        
    #пытаемся залогиниться
    print('пытаемся залогиниться')
    data = locate_image('login_conf.png')

    if data:
            pg.moveTo(data[0] + 5, data[1] + 5)
            pg.click()
            print('нажали кнопку логин')
            time.sleep(2)
            
            #вводим ид конференции
    data = locate_image('input_conf.png')
    if data:
                pg.moveTo(data[0] + 100, data[1] + 100)
                pg.click()
                time.sleep(3)
                pg.typewrite(str(conf_id))
                pg.press('enter')
                time.sleep(3)
    print('вводим код доступа')
    data = locate_image('input_code.png')
    if data:
                    pg.moveTo(data[0] + 100, data[1] + 100)
                    pg.click()
                    time.sleep(1)
                    pg.typewrite(str(conf_pass))
                    pg.press('enter')

                    time.sleep(16)
                    data = locate_image('poniatno.png')
                    if data:
                        pg.moveTo(data[0] + 5, data[1] + 5)
                        pg.click()
                        time.sleep(2)

                    data = locate_image('poniatno.png')
                    if data:
                        pg.moveTo(data[0] + 5, data[1] + 5)
                        pg.click()
                        time.sleep(1)

                    logfile("zoom started")
                    enable_sound()

                    time.sleep(5)
                    return 1



    print('zoom not opened')
    os.startfile(r''+zoomfolder)
    time.sleep(5)
    runzoom()


def getlastday(update):
    global lastday
    #print(lastday)
    if ((lastday == 0 ) or ( update == 1 ) ):
        f = open('lastday.txt', 'r')
        for lastday in f:
             print('берем дату из файла '+str(lastday))
        f.close()


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

    f = open('list.txt', 'r')
    try:
        for lastsong in f:
             print(lastsong)
    except:
        lastsong = 0
    f.close()

    
    #берем список файлов
    directory = kirtan_folder
    files = os.listdir(directory)      
    files = list(filter(lambda x: x.endswith('.mp3'), files))
    next_song=random.choice(files)

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


   
        
        
        
        