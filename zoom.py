import pyautogui as pg
import numpy as np
import os
import datetime
import schedule
import time
import pyaudio
import audioop
import subprocess
import csv

#conf_id = '8829424825'
#conf_pass = 'bnk'

conf_id = '81141237582'
conf_pass = '973133'
kirtan_folder = 'C:/kirtans/'
zoomfolder ='C:/Users/Администратор/AppData/Roaming/Zoom/bin/Zoom.exe'





global lastday
lastday = 0
p = pyaudio.PyAudio()
CHUNK = 1024
FORMAT = pyaudio.paInt16
RATE = 44100
silent_threshold = 10
time_wait = 50
device = 2

channels=p.get_device_info_by_index(device)
print(channels)

stream = p.open(format=FORMAT, channels=p.get_device_info_by_index(device).get('maxInputChannels'), rate=RATE,
                input=True, frames_per_buffer=CHUNK, input_device_index=device)


def zoomcount():
    zoomcount = 0
    p_tasklist = subprocess.Popen('tasklist.exe /fo csv',
                                  stdout=subprocess.PIPE,
                                  universal_newlines=True)

    pythons_tasklist = []
    for p in csv.DictReader(p_tasklist.stdout):

        if p['€¬п ®Ўа\xa0§\xa0'] == 'Zoom.exe':
            zoomcount = zoomcount + 1
            #print('enabled ')
            #print(p)

    return zoomcount

def isWindowsProcessRunning( exeName ) :

    process = subprocess.Popen(
        'tasklist.exe /FO CSV /FI "IMAGENAME eq %s"' % exeName,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        universal_newlines=True )
    out, err = process.communicate()
    try : return out.split("\n")[1].startswith('"%s"' % exeName)
    except : return False













def check_users_sound(time_wait):
    if (runzoom()):
        for x in range(time_wait):
            data = stream.read(CHUNK)
            threshold = audioop.max(data, 2)
            print(str(x) + ': ' + str(threshold))
            if threshold > silent_threshold:
                print("Sound found at index " + str(device))
                pause_kirtan()
                return 1
            time.sleep(1)
        print("Sound is off")
        print("play_kirtan ")
        play_kirtan()



def enable_sound():


        data = pg.locateOnScreen('mic_disabled.png',grayscale=True)
        if data:
            pg.moveTo(data[0] + 5, data[1] + 5)
            pg.click()
            time.sleep(1)

        data = pg.locateOnScreen('original_sound.png',grayscale=True)
        if data:
            pg.moveTo(data[0] + 5, data[1] + 5)
            pg.click()




def runzoom():
    #проверяем открыто ли окно зум
    #count = zoomcount()
    #if count == 2:
    #    return 1


    data = pg.locateOnScreen('zoom_opened.png',grayscale=True)
    if data:
        return 1
    print('не вижу открытое окно зум')



    data = pg.locateOnScreen('fulscreen.png')
    if data:
        pg.moveTo(data[0] + 5, data[1] + 5)
        pg.click()
        time.sleep(2)
        print('разворачиваем свернутое окно')
        return runzoom()
 
    data = pg.locateOnScreen('fulscreen_2.png')
    if data:
        pg.moveTo(data[0] + 5, data[1] + 5)
        pg.click()
        time.sleep(2)
        print('разворачиваем свернутое окно')
        return runzoom()
    
    
    
    data = pg.locateOnScreen('zoom_ok.png')
    if data:
        pg.moveTo(data[0] + 5, data[1] + 5)
        pg.click()
        time.sleep(2)
        print('нажимаем кнопку ОК в окне зум')
        return runzoom()
    
    

    
    print('пытаемся открыть зум в нижнем правом углу')    
    data = pg.locateOnScreen('zoom_shotcout.png')
   
    if data:
        pg.moveTo(data[0] + 5, data[1] + 5)
        pg.click()
        time.sleep(3)
        print('нажали на кнопку') 
        
        #проверяем может зум уже открыт
    print('проверяем может зум уже открыт')
    data = pg.locateOnScreen('disabled_login.png')
    if data:
            print('похоже зум уже открыт и свернут пытаемся развернуть')            
            data = pg.locateOnScreen('zoom_shotcout_big.png')
            if data:
                pg.moveTo(data[0] + 5, data[1] + 5)
                pg.click()
                time.sleep(1)
                pg.moveTo(data[0] +100, data[1] - 100)
                pg.click()
                time.sleep(1)
                print('нажали чтобы открыть зум')
                return runzoom()
       
        
    #пытаемся залогиниться
    print('пытаемся залогиниться')
    data = pg.locateOnScreen('login_conf.png')

    if data:
            pg.moveTo(data[0] + 5, data[1] + 5)
            pg.click()
            print('нажали кнопку логин')
            time.sleep(2)
            
            #вводим ид конференции
    data = pg.locateOnScreen('input_conf.png')
    if data:
                pg.moveTo(data[0] + 100, data[1] + 100)
                pg.click()
                time.sleep(3)
                pg.typewrite(str(conf_id))
                pg.press('enter')
                time.sleep(3)
    print('вводим код доступа')
    data = pg.locateOnScreen('input_code.png')
    if data:
                    pg.moveTo(data[0] + 100, data[1] + 100)
                    pg.click()
                    time.sleep(1)
                    pg.typewrite(str(conf_pass))
                    pg.press('enter')

                    time.sleep(16)
                    data = pg.locateOnScreen('poniatno.png')
                    if data:
                        pg.moveTo(data[0] + 5, data[1] + 5)
                        pg.click()
                        time.sleep(1)
                        pg.doubleClick()
                        time.sleep(2)



                    enable_sound()

                    time.sleep(5)
                    return 1




    print('zoom not opened')
    os.startfile(r''+zoomfolder)
    time.sleep(5)
    runzoom()


def getlastday(update):
    global lastday
    print(lastday)
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

    if ( (int(d_hour) == int(dt_hour) and int(d_minutes) >= 30 and int(dt_minutes) < 30) or (int(d_hour) > int(dt_hour)) ):
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
    print('проверяем может киртан уже играет')
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
    os.startfile(r''+kirtan_folder+str(kirtan_name))
    print('запускаем файл '+str(kirtan_name))

    return 1


        

def check_last_played():
    #проверяем какой киртан играл вчер
    f = open('list.txt', 'r')
    for lastsong in f:
        print(lastsong)
       
    f.close()
    
    
    #берем список файлов
    directory = kirtan_folder
    files = os.listdir(directory)      
    files = list(filter(lambda x: x.endswith('.mp3'), files))
    #print(files)

    
   
    try:
        index = files.index(lastsong)
    except:
        index = 0
        
    #проверяем день тот же что и вчера или изменился
        
    day = getlastday(1)
    
    
    if (day==0):
        return lastsong

    
    next_index = int(index)+1
    
    try:
        next_song = files[next_index]
    except:
        next_index = 0  
        next_song = files[0]
    
    #print(next_song)
    f = open('list.txt', 'w')
    f.write(next_song)
    f.close()
    return next_song
    



# schedule.every().day.at("00:00").do(pause_kirtan)

#проверяем включен ли звук каждые 100 секунд


if (runzoom()):
   enable_sound()

while True:

   check_users_sound(time_wait)
   time.sleep(1)
   if (getlastday(0)):
       pause_kirtan()

   
        
        
        
        