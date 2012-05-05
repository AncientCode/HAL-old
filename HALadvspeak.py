import __builtin__
__builtin__._HAL_ADV_SPEAK__REGISTERED_ = True

from urllib import urlencode
import threading
import time
try:
    import pydshow
except ImportError:
    pass

langmap = {
    'en-us': 'ukenglish',
    'en-uk': 'ukenglish',
}

def get_speak(text, volume=100, speed=175, gender=True, lang='en-us'):
    words = text.split()
    temp = []
    stuff = []
    while words:
        temp.append(words.pop(0))
        if len(temp) == 24:
            stuff.append(' '.join(temp))
            temp = []
    stuff.append(' '.join(temp))
    args = dict(apikey='8d1e2e5d3909929860aede288d6b974e', format='mp3',
                action='convert', voice='ukenglish'+('male' if gender else 'female'),
                speed=str((speed+85)/26-10))
    return stuff, args

def speak_async(text, volume=100, speed=175, gender=True, lang='en-us', lock=threading.Lock()):
    stuff, args = get_speak(text, volume, speed, gender, lang)
    for i in stuff:
        args['text'] = i
        dshow = pydshow.DirectShow('http://api.ispeech.org/api/rest?'+urlencode(args))
        dshow.PlayFile(False, 0, False)
        #dshow.SetVolume(8000+volume/2*10)
        while dshow.isPlaying():
            if not lock.acquire(0):
                dshow.Stop()
                return
            time.sleep(0.2)
            lock.release()

def speak_sync(text, volume=100, speed=175, gender=True, lang='en-us'):
    stuff, args = get_speak(text, volume, speed, gender, lang)
    for i in stuff:
        args['text'] = i
        dshow = pydshow.DirectShow('http://api.ispeech.org/api/rest?'+urlencode(args))
        #dshow.SetVolume(9500+volume/2*10)
        dshow.PlayFile(True, 0, False)

# gender: True for male and False for female
def speak(text, block=True, volume=100, speed=175, gender=True, lang='en-us'):
    if block == False:
        lock = threading.Lock()
        threading.Thread(target=speak_async, kwargs=dict(text=text, lock=lock,
                                                         volume=volume, speed=speed,
                                                         gender=gender, lang=lang)).start()
        return lock
    else:
        speak_sync(text, volume, speed, gender, lang)

def stop_speaking(handle):
    try:
        handle.acquire()
    except AttributeError:
        # Wrong Handle...
        pass

if __name__ == '__main__':
    text = "Open a file, returning an object of the file type described in section File Objects. If the file cannot be opened, IOError is raised. When opening a file, it's preferable to use open() instead of invoking the file constructor directly."
    print 'Blocking...'
    #speak(text, volume=100, speed=300)
    print 'Cut after 5 sec'
    h = speak(text, volume=100, speed=300, block=False)
    time.sleep(5)
    stop_speaking(h)

