from assistant.speech import SpeechEngine

_SPEECH = SpeechEngine()


def set_status_callback(callback):
    _SPEECH.set_status_callback(callback)


def speak(text):
    _SPEECH.speak(text)
