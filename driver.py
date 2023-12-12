# TODO: import this elsewhere or set it up first
# from facial_recognition import facial_req
# import speech_recognition as sr
# print(sr.__version__)

import pyttsx3
eng = pyttsx3.init()
eng.setProperty('rate',70)
voices = eng.getProperty('voices')
for v in voices:
  eng.setProperty('voice', v.id)
  eng.say("Hello who is that over there?")
eng.runAndWait()

def driver():
  print("asdf")


if __name__ == "driver.py":
  driver()
