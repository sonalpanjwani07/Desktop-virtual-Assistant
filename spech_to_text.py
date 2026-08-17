from assistant.speech import SpeechEngine

_SPEECH = SpeechEngine()


def set_status_callback(callback):
    _SPEECH.set_status_callback(callback)


def spech_to_text():
    return _SPEECH.listen_once(timeout=5, phrase_time_limit=10)


