# Voice-Only Mode

Run:

```bash
python main.py --voice-only
# or
python main_voice_only.py
```

Voice-only mode does not open the GUI and does not print command responses to the terminal. It listens through the microphone and speaks responses through text-to-speech.

If voice dependencies or microphone access are missing, Jarvis will say so and exit. Install `SpeechRecognition`, `pyttsx3`, and platform audio dependencies first.
