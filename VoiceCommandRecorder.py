import os
import wave
import pyaudio
import csv
from datetime import datetime

# Configuration
AUDIO_FOLDER = "voice_commands"  # Folder to save audio files
CSV_FILE = "voice_commands.csv"  # CSV file to store metadata
COMMANDS = ["start", "stop", "left", "right", "up", "down"]  # List of commands
LANGUAGES = ["English", "Turkish"]  # Supported languages
SAMPLE_RATE = 44100  # Audio sample rate
CHUNK = 1024  # Audio chunk size
FORMAT = pyaudio.paInt16  # Audio format
CHANNELS = 1  # Mono audio

# Initialize PyAudio
audio = pyaudio.PyAudio()

import threading

class VoiceCommandRecorder:
    def __init__(self):
        self.recording = False
        self.frames = []
        self.command = ""
        self.language = ""
        self.speaker = ""
        self.lock = threading.Lock()

    def start_recording(self, command, language, speaker):
        with self.lock:
            self.command = command
            self.language = language
            self.speaker = speaker
            self.recording = True
            self.frames = []

            self.stream = audio.open(format=FORMAT, channels=CHANNELS,
                                     rate=SAMPLE_RATE, input=True,
                                     frames_per_buffer=CHUNK)
            print("Recording started...")

            while self.recording:
                data = self.stream.read(CHUNK)
                self.frames.append(data)


    def stop_recording(self):
        if not self.recording:
            return
        self.recording = False
        self.stream.stop_stream()
        self.stream.close()
        print("Recording stopped.")

        # Generate a unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(AUDIO_FOLDER, f"{self.command}_{self.language}_{self.speaker}_{timestamp}.wav")

        # Save the recorded frames as a WAV file
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b''.join(self.frames))  # This was missing!

        # Save metadata to CSV
        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.command, self.speaker, self.language, filename])

        print(f"Saved: {filename}")
