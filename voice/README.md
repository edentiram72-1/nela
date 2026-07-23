# Voice Module

## Purpose

Voice provides interfaces for future wake word detection, microphone input, speech recognition, and speech synthesis.

## Responsibilities

- Capture audio.
- Detect wake words.
- Convert speech to text.
- Convert text to speech.

## Public API

- `Microphone.listen()`
- `WakeWordDetector.is_wake_word(audio)`
- `SpeechToText.transcribe(audio)`
- `TextToSpeech.synthesize(text)`

## Known Limitations

- No real audio implementation exists yet.
- No speech provider is configured yet.

## Future Improvements

- Local wake word engine.
- Streaming speech recognition.
- Low-latency text-to-speech.
- Voice activity detection.

