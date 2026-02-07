import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import random
import os
from openai import OpenAI
from config import apikey
import json
import datetime

# ---------------- CONFIG ----------------
client = OpenAI(api_key=apikey)

engine = pyttsx3.init()
engine.setProperty("rate", 170)

chatStr = ""

# ---------------- SPEAK ----------------
last_reply = ""

def say(text):
    global last_reply
    last_reply = text
    engine = pyttsx3.init("sapi5")
    voices = engine.getProperty("voices")
    engine.setProperty("voice", voices[0].id)
    engine.setProperty("rate", 170)
    engine.say(text)
    engine.runAndWait()
# ---------------- CHAT ----------------
def chat(query):
    global chatStr
    chatStr += f"User: {query}\nJarvis: "

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are Jarvis, a helpful AI assistant."},
                {"role": "user", "content": chatStr}
            ]
        )

        reply = response.choices[0].message.content
        chatStr += reply + "\n"
        print(reply)
        say(reply)
        last_reply=reply
        

    except Exception as e:
        print(e)
        say("Sorry sir, there was an error.")

# ---------------- AI FILE WRITER ----------------
def ai(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        text = response.choices[0].message.content

        if not os.path.exists("OpenAI"):
            os.mkdir("OpenAI")

        filename = f"OpenAI/prompt_{random.randint(1,9999)}.txt"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(text)

        say("I have saved the response sir.")

    except Exception as e:
        print(e)

# ---------------- LISTEN ----------------
def takeCommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)

    try:
        print("Recognizing...")
        query = r.recognize_google(audio, language="en-in")
        print(f"User said: {query}")
        return query

    except Exception:
        return ""
    
# ---------------- MEMORY FUNCTIONS ----------------
MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({"conversations": []}, f)
        return []

    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)["conversations"]

def save_memory(user_text, jarvis_text):
    memory = load_memory()

    memory.append({
        "time": str(datetime.datetime.now()),
        "user": user_text,
        "jarvis": jarvis_text
    })

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"conversations": memory}, f, indent=4)


# ---------------- MAIN ----------------
if __name__ == "__main__":
    print("Welcome to Jarvis A.I")
    say("Welcome to Jarvis A I")

    while True:
        query = takeCommand().lower()
        

        if "hello jarvis" in query:
            print("hello sir, how can I help you?")
            say("hello sir, how can I help you?")

        elif "remember" in query.lower():
            fact = query.lower().replace("jarvis remember", "").strip()
            if fact == "":
                say("What should I remember?")
            else:
                save_memory("FACT", fact)
                say("Okay, I will remember that")

        elif "open youtube" in query:
            say("Opening youtube")
            webbrowser.open("https://youtube.com")

        elif "open google" in query:
            say("Opening Google")
            webbrowser.open("https://google.com")

        elif "time" in query:
            time = datetime.datetime.now().strftime("%H:%M")
            say(f"Sir, the time is {time}")

        elif "using artificial intelligence" in query:
            ai(query)

        elif "reset chat" in query:
            chatStr = ""
            say("Chat reset sir")

        elif "quit" in query or "exit" in query:
            say("Goodbye sir")
            break

        elif query != "":
            print(query)
            chat(query)
            save_memory(query, last_reply)
        
    

