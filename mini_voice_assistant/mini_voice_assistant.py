import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import os
import tkinter as tk
from tkinter import scrolledtext

# Initialize recognizer and engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Function to speak
def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except KeyboardInterrupt:
        print("Program interrupted.")
        exit(0)
    except Exception as e:
        print(f"Error in speech: {e}")

# Function to take command
def take_command():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            query = recognizer.recognize_google(audio)
        except sr.WaitTimeoutError:
            speak("No speech detected. Please try again.")
            return ""
        except sr.UnknownValueError:
            speak("Sorry, I did not catch that.")
            return ""
        except sr.RequestError:
            speak("Network error. Check connection.")
            return ""
        return query.lower()

# Function when button clicked
def run_assistant():
    output_text.insert(tk.END, "Assistant: Hello, how can I assist you today?\n")
    speak("Hello, how can I assist you today?")

    query = take_command()
    if query:
        output_text.insert(tk.END, f"You: {query}\n")

        if "time" in query:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The current time is {current_time}"
        elif "date" in query:
            today = datetime.date.today().strftime("%B %d, %Y")
            response = f"Today's date is {today}"
        elif "open google" in query:
            response = "Opening Google"
            webbrowser.open("https://www.google.com")
        elif "play music" in query:
            music_dir = "C:\\Users\\Public\\Music"
            songs = os.listdir(music_dir)
            if songs:
                os.startfile(os.path.join(music_dir, songs[0]))
                response = "Playing music"
            else:
                response = "No music files found"
        elif "search for" in query:
            search_query = query.replace("search for", "").strip()
            if search_query:
                response = f"Searching for {search_query}"
                webbrowser.open(f"https://www.google.com/search?q={search_query}")
            else:
                response = "What should I search for?"
        elif "exit" in query or "quit" in query or "stop" in query:
            response = "Goodbye!"
            output_text.insert(tk.END, f"Assistant: {response}\n")
            speak(response)
            app.quit()
            return
        else:
            response = "Sorry, I am not able to help with that yet."

        output_text.insert(tk.END, f"Assistant: {response}\n")
        speak(response)

# GUI Setup
app = tk.Tk()
app.title("Voice AI Assistant")
app.geometry("500x400")

start_button = tk.Button(app, text="Talk to Assistant", font=("Arial", 14), command=run_assistant)
start_button.pack(pady=20)

output_text = scrolledtext.ScrolledText(app, font=("Arial", 12))
output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

app.mainloop()
