import pyttsx3
import os

def setup():
  if os.path.exists("encodings.pickle"):
    print("Found encodings")
  else:
    import shutil
    dest = os.path.join(os.getcwd(), "encodings.pickle")
    shutil.copy2("facial_recognition/encodings.pickle", dest)
    print("Copyied encodings")
    
  from facial_recognition import facial_req

def cleanup():
  try:
    os.remove("encodings.pickle")
  except Exception as e:
    print(f"Error:\t{e}")

def init_engine():
  eng = pyttsx3.init()
  eng.setProperty('rate',160)
  return eng

def set_voice_and_speak(eng, text):
  voices = eng.getProperty('voices')
  eng.setProperty('voice', voices[16].id)
  eng.say(text)


setup()
engine = init_engine()
set_voice_and_speak(engine, "Hello, what is your name?")
engine.runAndWait()
cleanup()
