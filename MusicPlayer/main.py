import pyttsx3
import speech_recognition as sr
import pygame
from fuzzywuzzy import fuzz
import json

import searcher
import downloader

import simpleaudio as sa
import random
import threading

recognizer = sr.Recognizer()
engine = pyttsx3.init()

pygame.init()
pygame.mixer.init()

activated = False
looping = False
play_random = False
listening = False

song_playing = ""
songs_played = []

def find_song_file(text):
    with open("song_data.json", "r") as f:
            existing = json.load(f)

    for key, value in existing.items():
        similarityWhole = fuzz.ratio(key, text)
        similarityHalf = fuzz.ratio(key.split(" by ")[0], text)


        print(f"{similarityWhole} : {similarityHalf}")

        if similarityWhole > 80 or similarityHalf > 80:
            song_name = value.get("name")

            return song_name, key
    
    return None, None

def start_download(og_text):
    print(f"Finding {og_text}")
    wave_obj = sa.WaveObject.from_wave_file("./Audio/loading.wav")
    play_obj = wave_obj.play()
    text = og_text
    
    if not "instrumental" in og_text:
        text = og_text + " lyric video"
    link, title = searcher.search(text)

    if link:
        print(f"Downloading Song: {title}")
        file_name = downloader.download(link)
        # try:
        #     source = f"/home/zeglexa/Downloads/{title} 4.mp3"
        #     source = source.replace('"', "_")
        #     print(source)
        #     while not os.path.exists(source):
        #         print("Still waiting for file...")
        #         if " 4.mp3" in source:
        #             source = source.replace(" 4.mp3", ".mp3")
        #         else:
        #             source = source.replace(".mp3", " 4.mp3")
        #         time.sleep(1)
        #     destination_folder = "./Songs"

        #     shutil.move(source, os.path.join(destination_folder, os.path.basename(source)))
        # except FileNotFoundError:
        #     print("File not found :(")
        #     return
        

                # Step 1: Load existing data
        with open("song_data.json", "r") as f:
            existing = json.load(f)

        # Step 2: Modify or append
        existing[og_text] = {
            "name": file_name
        }

        # Step 3: Save it back
        with open("song_data.json", "w") as f:
            json.dump(existing, f, indent=4)

        play_obj.stop()
        pygame.mixer_music.unpause()
    else:
        print("Link failed :(")
        pygame.mixer_music.unpause()
        play_obj.stop()

def play_song(text):
    global song_playing
    song_name, key = find_song_file(text)

    if song_name == None:
        print("Failed to find Song")
        engine.say(f"Sorry, but {text} could not be found.")
        engine.runAndWait()
        pygame.mixer_music.unpause()
        return

    engine.say(f"Ok! Playing {key}!")
    engine.runAndWait()
    print("Playing Song")

    song_playing = song_name
    pygame.mixer_music.unpause()
    pygame.mixer_music.load(f"./Songs/{song_name}")
    pygame.mixer_music.play()

def play_random_song():
    with open("song_data.json", "r") as f:
        existing = json.load(f)
                
    song_name = random.choice(list(existing.values())).get("name")

    if song_name in songs_played:
        print("NO! NO REPEATS!!")
        play_random_song()
        return
    
    songs_played.append(song_name)
    pygame.mixer_music.unpause()
    pygame.mixer_music.load(f"./Songs/{song_name}")
    pygame.mixer_music.play()

def queue_song(text):
    song_name, key = find_song_file(text)

    engine.say(f"Ok! Queuing {key}!")
    engine.runAndWait()

    pygame.mixer_music.queue(f"./Songs/{song_name}")

def mixer_thread():
    while True:
        if ( not pygame.mixer_music.get_busy() ) and ( not activated ):
            if looping and song_playing != "":
                pygame.mixer_music.unpause()
                pygame.mixer_music.load(f"./Songs/{song_playing}")
                pygame.mixer_music.play()
            if play_random:
                play_random_song()

thread = threading.Thread(target=mixer_thread)
thread.start()

while True:
    if ( not pygame.mixer_music.get_busy() ) and ( not activated ):
        if looping and song_playing != "":
            pygame.mixer_music.unpause()
            pygame.mixer_music.load(f"./Songs/{song_playing}")
            pygame.mixer_music.play()
        if play_random:
            play_random_song()
                
            
    try:
        with sr.Microphone() as mic:
            recognizer.adjust_for_ambient_noise(mic, duration=0.2)
            print("Listening...")
            audio = recognizer.listen(mic)

            text = recognizer.recognize_google(audio)
            text = text.lower()

            if text == "hey speaker" and not activated:
                print("ACTIVATED")
                activated = True
                pygame.mixer_music.pause()
                
                wave_obj = sa.WaveObject.from_wave_file("./Audio/activate.wav")
                play_obj = wave_obj.play()
                play_obj.wait_done()
                pass
            elif activated:
                activated = False
                print(f"You're commanding: {text}")

                if text.startswith("download"):
                    text = text[9:]

                    if len(text) <= 4:
                        continue

                    print("Attempting to download: " + text)
                    start_download(text)

                elif text.startswith("play"):
                    text = text[5:]
                    print("Attempting to play song: " + text)
                    play_song(text)

                elif text.startswith("stop"):
                    pygame.mixer_music.pause()

                elif text.startswith("resume"):
                    pygame.mixer_music.unpause()

                elif text.startswith("queue"):
                    text = text[6:]
                    print("Attempting to queue a song: " + text)
                    queue_song(text)
                    pygame.mixer_music.unpause()

                elif text.startswith("loop"):
                    looping = not looping
                    print(f"Looping: {looping}")

                elif text.startswith("random"):
                    play_random = not play_random
                    print(f"Play Random Songs: {play_random}")

                else:
                    pygame.mixer_music.unpause()

            else:
                print(f"You yapped: {text}")
                pygame.mixer_music.unpause()

    except sr.UnknownValueError:
        print("I ain't hear nun ??")
        continue
