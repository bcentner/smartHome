import pyttsx3
import os
import time
from facial_req import FaceRecognition

def setup():
  if os.path.exists("encodings.pickle"):
    print("Found encodings")
  else:
    import shutil
    dest = os.path.join(os.getcwd(), "encodings.pickle")
    shutil.copy2("facial_recognition/encodings.pickle", dest)
    print("Copyied encodings")

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
face_system = FaceRecognition()
face_system.start()
time.sleep(1)
try:
  while True:
    if face_system.new_person_found:
      set_voice_and_speak(engine, "Hello, what is your name?")
      engine.runAndWait()
    time.sleep(1)
except Exception as e:
  print(f"Exception:\t{e}")
finally:
  face_system.stop()
  cleanup()
