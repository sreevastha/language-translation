import os
import uuid
import tkinter as tk
from tkinter import messagebox, scrolledtext
from gtts import gTTS
import pygame
import speech_recognition as sr
from googletrans import Translator, LANGUAGES
from langdetect import detect
from sklearn.feature_extraction.text import TfidfVectorizer
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Embedding, Bidirectional
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from PIL import Image, ImageTk

# Initialize translator and pygame mixer
translator = Translator()
pygame.mixer.init()
tokenizer = Tokenizer(num_words=10000)

# Define the LSTM model (example setup for further expansion)
def create_lstm_model():
    model = Sequential([
        Embedding(input_dim=10000, output_dim=64, input_length=50),
        Bidirectional(LSTM(64, return_sequences=True)),
        LSTM(32),
        Dense(32, activation='relu'),
        Dense(1, activation='sigmoid')  # For binary classification
    ])
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

lstm_model = create_lstm_model()

def classify_language(text):
    """Detect the language of the input text."""
    try:
        detected_language = detect(text)
        return detected_language
    except:
        return "Unknown"

def preprocess_text(text):
    """Tokenizes and pads the input text for the LSTM model."""
    tokenizer.fit_on_texts([text])
    sequences = tokenizer.texts_to_sequences([text])
    padded_sequence = pad_sequences(sequences, maxlen=50)
    print("Padded Sequence:", padded_sequence)
    return padded_sequence

def translator_function(text, to_language):
    """Translates text using Google Translate."""
    translated_text = translator.translate(text, dest=to_language)
    return translated_text.text

def text_to_voice(text_data, to_language):
    """Converts text to speech and plays it."""
    filename = f"{uuid.uuid4()}.mp3"
    myobj = gTTS(text=text_data, lang=to_language, slow=False)
    myobj.save(filename)

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    pygame.mixer.music.unload()
    os.remove(filename)

def translate_text():
    """Handles translation and speech for text input."""
    input_text = text_input.get("1.0", tk.END).strip()
    if not input_text:
        messagebox.showwarning("Warning", "Please enter some text to translate.")
        return

    input_language = classify_language(input_text)
    input_lang_name = LANGUAGES.get(input_language, 'Unknown')
    detected_lang_label.config(text=f"Detected input language: {input_lang_name}")
    preprocess_text(input_text)

    to_language = language_var.get().split(' - ')[0]
    translated_text = translator_function(input_text, to_language)
    translated_text_display.config(state="normal")
    translated_text_display.delete("1.0", tk.END)
    translated_text_display.insert(tk.END, translated_text)
    translated_text_display.config(state="disabled")

    text_to_voice(translated_text, to_language)

def translate_voice():
    """Handles translation and speech for voice input with speech-to-text conversion."""
    rec = sr.Recognizer()
    with sr.Microphone() as source:
        messagebox.showinfo("Info", "Please speak now...")
        rec.pause_threshold = 1
        try:
            audio = rec.listen(source, timeout=5)
            messagebox.showinfo("Info", "Processing audio...")

            input_text = rec.recognize_google(audio)
            text_input.delete("1.0", tk.END)
            text_input.insert(tk.END, input_text)

            input_lang_name = LANGUAGES.get(classify_language(input_text), 'Unknown')
            detected_lang_label.config(text=f"Detected input language: {input_lang_name}")
            preprocess_text(input_text)

            to_language = language_var.get().split(' - ')[0]
            translated_text = translator_function(input_text, to_language)
            translated_text_display.config(state="normal")
            translated_text_display.delete("1.0", tk.END)
            translated_text_display.insert(tk.END, translated_text)
            translated_text_display.config(state="disabled")

            text_to_voice(translated_text, to_language)

        except sr.UnknownValueError:
            messagebox.showerror("Error", "Could not understand the audio. Please try again.")
        except sr.RequestError:
            messagebox.showerror("Error", "Could not request results from the speech recognition service.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

# GUI Setup
root = tk.Tk()
root.title("Text & Voice Translator")
root.geometry("500x600")
root.configure(bg="#EAECEE")

# Load Icons
text_icon = ImageTk.PhotoImage(Image.open("text_icon.png").resize((25, 25)))
voice_icon = ImageTk.PhotoImage(Image.open("voice_icon.png").resize((25, 25)))

# Target Language Selection
language_var = tk.StringVar(value="en - English")
language_options = [f"{code} - {name.title()}" for code, name in LANGUAGES.items()]
tk.Label(root, text="Select Target Language:", font=("Helvetica", 12, "bold"), bg="#EAECEE").pack(pady=5)
lang_dropdown = tk.OptionMenu(root, language_var, *language_options)
lang_dropdown.config(bg="#AED6F1", font=("Helvetica", 10))
lang_dropdown.pack()

# Detected Language Display
detected_lang_label = tk.Label(root, text="Detected input language: ", font=("Helvetica", 10, "italic"), bg="#EAECEE")
detected_lang_label.pack(pady=5)

# Text Input
tk.Label(root, text="Enter Text to Translate:", font=("Helvetica", 12, "bold"), bg="#EAECEE").pack(pady=5)
text_input = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=5)
text_input.pack(pady=5)

# Translate Buttons
text_translate_button = tk.Button(root, text="Translate Text", command=translate_text, image=text_icon, compound=tk.LEFT, bg="#76D7C4", font=("Helvetica", 10, "bold"))
text_translate_button.pack(pady=5)

voice_translate_button = tk.Button(root, text="Translate Voice", command=translate_voice, image=voice_icon, compound=tk.LEFT, bg="#76D7C4", font=("Helvetica", 10, "bold"))
voice_translate_button.pack(pady=5)

# Translated Text Display
tk.Label(root, text="Translated Text:", font=("Helvetica", 12, "bold"), bg="#EAECEE").pack(pady=5)
translated_text_display = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=5, state="disabled")
translated_text_display.pack(pady=5)

root.mainloop()
