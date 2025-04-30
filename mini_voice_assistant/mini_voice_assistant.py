import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import os
import tkinter as tk
from tkinter import scrolledtext
import threading
import requests
import asyncio
import winsound  # For adding sound effects
from time import sleep

# Initialize recognizer and engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Configure pyttsx3 for faster and clearer speech
engine.setProperty('rate', 180)  # Faster speech rate
engine.setProperty('volume', 1)  # Full volume
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)  # Change to a different voice if you prefer

# Speak Function (Optimized for faster response)
def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Error in speech: {e}")

# Listen Function (Optimized for faster listening)
def listen_once(timeout=5, phrase_time_limit=5):
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=1)
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            query = recognizer.recognize_google(audio)
            return query.lower()
        except sr.WaitTimeoutError:
            speak("No speech detected. Please try again.")
            return ""
        except sr.UnknownValueError:
            speak("Sorry, I did not catch that.")
            return ""
        except sr.RequestError:
            speak("Network error. Check connection.")
            return ""

# Internet Connection Check
def is_connected():
    try:
        response = requests.get('https://www.google.com', timeout=3)
        return response.status_code == 200
    except (requests.ConnectionError, requests.Timeout):
        return False

# Greet the User
def greet_user():
    hour = datetime.datetime.now().hour
    if 5 <= hour < 12:
        return "Good morning, sir. How can I assist you today?"
    elif 12 <= hour < 18:
        return "Good afternoon, sir. How can I assist you today?"
    else:
        return "Good evening, sir. How can I assist you today?"

# Async Weather Fetch
async def get_weather(city_name=None):
    api_key = "87309e1428e346176c28db0320299fbd"
    base_url = "https://api.openweathermap.org/data/2.5/weather"

    if not city_name:
        city_name = await get_current_city()

    params = {
        "q": city_name,
        "appid": api_key,
        "units": "metric"
    }
    try:
        response = await asyncio.to_thread(requests.get, base_url, params=params)
        data = response.json()

        if data["cod"] != 200:
            return "City not found. Please try again."

        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]
        return f"The temperature in {city_name} is {temperature}°C with {description}."
    except Exception:
        return "Unable to retrieve weather data right now."

# Async Current City (IP-based Location Detection)
async def get_current_city():
    try:
        ip_info = await asyncio.to_thread(requests.get, 'https://ipinfo.io/json')
        ip_info = ip_info.json()
        city = ip_info.get('city')
        if city:
            return city
        else:
            return "Chennai"  # Fallback
    except Exception:
        return "Chennai"  # Fallback

# Async News Fetch
async def get_news():
    api_key = "c8106278052a44c5b5d2d8288b2abcea"  # Your NewsAPI key
    base_url = "https://newsapi.org/v2/top-headlines"
    params = {
        "country": "us",  # You can change this to your country code like "in" for India
        "apiKey": api_key
    }
    
    try:
        response = await asyncio.to_thread(requests.get, base_url, params=params)
        data = response.json()

        if data["status"] == "ok":
            articles = data["articles"][:5]  # Get top 5 latest news articles
            news = "Here are the latest news headlines:\n"
            for article in articles:
                news += f"{article['title']}\n"
            return news
        else:
            return "Sorry, I couldn't fetch the news right now."
    except Exception:
        return "Unable to retrieve news data right now."

# Command Handler
def handle_command():
    # Sound for starting to listen
    winsound.Beep(1000, 200)  # Plays a sound to indicate listening

    loading_label.config(text="Listening...")
    query = listen_once(timeout=5, phrase_time_limit=5)
    loading_label.config(text="")  # Hide loading after listening

    if query:
        output_text.insert(tk.END, f"You: {query}\n")
        output_text.yview(tk.END)

        response = ""

        # Small Talk
        if "hello" in query:
            response = "Hello, sir! How can I assist you today?"
        elif "good morning" in query:
            response = "Good morning, sir! Hope you have a wonderful day!"
        elif "good afternoon" in query:
            response = "Good afternoon, sir! How can I assist you?"
        elif "good evening" in query:
            response = "Good evening, sir! What can I do for you?"
        elif "how are you" in query:
            response = "I'm functioning perfectly, thank you for asking."
        elif "thank you" in query or "thanks" in query:
            response = "You're welcome, sir!"
        elif "i love you" in query:
            response = "I love you too, sir. But remember, I'm just a machine. 😎"

        # Main Features
        elif "time" in query:
            current_time = datetime.datetime.now().strftime("%I:%M %p")
            response = f"The current time is {current_time}"

        elif "date" in query:
            today = datetime.date.today().strftime("%B %d, %Y")
            response = f"Today's date is {today}"

        elif "open google" in query:
            response = "Opening Google now"
            if is_connected():
                webbrowser.open("https://www.google.com")
            else:
                response = "No internet connection. Please check your connection."

        elif "play music" in query:
            music_dir = "C:\\Users\\Public\\Music"
            songs = os.listdir(music_dir)
            if songs:
                os.startfile(os.path.join(music_dir, songs[0]))
                response = "Playing music"
            else:
                response = "No music files found"

        elif "pause music" in query:
            # Pausing music functionality (requires additional integration with a media player)
            response = "Music paused."

        elif "skip music" in query:
            # Skip music functionality (requires additional integration with a media player)
            response = "Skipping to next track."

        elif "weather" in query:
            if is_connected():
                response = asyncio.run(get_weather())
            else:
                response = "No internet connection. Cannot fetch weather info."

        elif "news" in query:
            if is_connected():
                response = asyncio.run(get_news())
            else:
                response = "No internet connection. Cannot fetch news."

        elif "exit" in query or "quit" in query or "stop" in query:
            response = "Goodbye, sir!"
            output_text.insert(tk.END, f"Assistant: {response}\n")
            speak(response)
            app.quit()
            return

        else:
            response = "Sorry, I am not able to help with that yet."

        output_text.insert(tk.END, f"Assistant: {response}\n")
        output_text.yview(tk.END)
        speak(response)

# GUI Setup
app = tk.Tk()
app.title("Jarvis - Voice Assistant")
app.geometry("800x600")
app.configure(bg="#232f3e")  # Dark Amazon-like color

# Center window
screen_width = app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
window_width = 800
window_height = 600
center_x = int(screen_width / 2 - window_width / 2)
center_y = int(screen_height / 2 - window_height / 2)
app.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

# Title
title_label = tk.Label(app, text="Jarvis - Your Personal Assistant", font=("Helvetica", 20, "bold"), fg="white", bg="#232f3e")
title_label.pack(pady=10)

# Loading Animation Label
loading_label = tk.Label(app, text="", font=("Helvetica", 14), fg="cyan", bg="#232f3e")
loading_label.pack()

# Circular Button for Interaction
start_button = tk.Button(
    app,
    text="🎙",
    font=("Helvetica", 20),
    fg="white",
    bg="#1DB954",  # Green like Alexa's icon color
    activebackground="#1DB954",
    activeforeground="white",
    command=lambda: threading.Thread(target=handle_command).start(),
    relief="raised",
    bd=5,
    width=10,
    height=2,
    borderwidth=3,
    padx=10
)
start_button.pack(pady=20)

# Output Area
output_text = scrolledtext.ScrolledText(
    app,
    font=("Consolas", 13),
    bg="#2d2d2d",
    fg="#dcdcdc",
    insertbackground="white",
    wrap=tk.WORD
)
output_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Run Assistant function
def run_assistant():
    greeting = greet_user()
    output_text.insert(tk.END, f"Assistant: {greeting}\n")
    output_text.yview(tk.END)
    speak(greeting)
    handle_command()

app.mainloop()