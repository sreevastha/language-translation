import os
import time
import pygame
from gtts import gTTS
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
import uuid

translator = Translator()  # Initialize the translator module.
pygame.mixer.init()  # Initialize the mixer module.

def translator_function(text, to_language):
    """Translates text using Google Translate."""
    translated_text = translator.translate(text, dest=to_language)
    return translated_text.text

def text_to_voice(text_data, to_language):
    """Converts text to speech and plays it."""
    filename = f"{uuid.uuid4()}.mp3"  # Generate unique filename
    myobj = gTTS(text=text_data, lang=to_language, slow=False)
    myobj.save(filename)

    # Load and play the audio file
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    # Wait for the audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Close the audio file before deletion
    pygame.mixer.music.unload()

    # Delete the audio file
    os.remove(filename)

def main_process(to_language):
    """Main process for continuous translation and speech output."""
    while True:
        input_type = input("Enter 't' for text input or 'v' for voice input: ")

        if input_type.lower() == 't':  # Text input
            spoken_text = input("Please enter the text you want to translate: ")
        elif input_type.lower() == 'v':  # Voice input
            rec = sr.Recognizer()
            with sr.Microphone() as source:
                print("Listening...")
                rec.pause_threshold = 1
                audio = rec.listen(source, phrase_time_limit=10)
                print("Processing...")
                try:
                    spoken_text = rec.recognize_google(audio)
                except Exception as e:
                    print("Error:", e)
                    continue  # Restart the loop if speech recognition fails
        else:
            print("Invalid input type. Please enter 't' for text or 'v' for voice.")
            continue

        print("Translating...")
        translated_text = translator_function(spoken_text, to_language)
        print("Translated text:", translated_text)

        text_to_voice(translated_text, to_language)

        # Ask if the user wants to translate again
        another_translation = input("Do you want to translate something else? (y/n): ")
        if another_translation.lower() != 'y':
            break  # Exit the loop if the user doesn't want to translate again

# Example usage:
to_language = input("Please enter the target language (e.g., 'en' for English): ")
main_process(to_language)
