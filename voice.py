"""
voice.py

Beginner-friendly voice module:
- Speech-to-text (SpeechRecognition)
- Text-to-speech (pyttsx3)
- Optional wake word gating
- Safe status callbacks for UI ("Idle", "Listening...", "Thinking...", "Speaking...")

This file is standalone and testable:
    python voice.py
"""

from __future__ import annotations

import os
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

try:
    import speech_recognition as sr
except Exception:
    sr = None  # type: ignore

try:
    import pyttsx3
except Exception:
    pyttsx3 = None  # type: ignore


StatusCallback = Callable[[str], None]


@dataclass
class VoiceConfig:
    # Recognition
    stt_language: str = os.getenv("ASSISTANT_STT_LANG", "en-US").strip() or "en-US"
    timeout: int = int(os.getenv("ASSISTANT_LISTEN_TIMEOUT", "6") or "6")
    phrase_time_limit: int = int(os.getenv("ASSISTANT_PHRASE_TIME_LIMIT", "10") or "10")
    mic_name: str = os.getenv("ASSISTANT_MIC_NAME", "").strip()  # partial name match

    # Wake word (optional)
    wake_enabled: bool = os.getenv("ASSISTANT_WAKE_ENABLED", "0").strip().lower() in {"1", "true", "yes", "on"}
    wake_word: str = os.getenv("ASSISTANT_WAKE_WORD", "").strip().lower()

    # Calibration
    calibration_ttl_s: float = float(os.getenv("ASSISTANT_CALIB_TTL_S", "45") or "45")
    calibration_duration_s: float = float(os.getenv("ASSISTANT_CALIB_DUR_S", "0.6") or "0.6")

    # TTS
    tts_rate_delta: int = int(os.getenv("ASSISTANT_TTS_RATE_DELTA", "-35") or "-35")  # negative = slower


class Voice:
    """
    A small, reliable voice helper.

    Typical usage:
        voice = Voice()
        voice.set_status_callback(ui_status_setter)
        text = voice.listen_once()
        voice.speak("Hello")
    """

    def __init__(self, config: Optional[VoiceConfig] = None):
        self.cfg = config or VoiceConfig()
        self._status_cb: Optional[StatusCallback] = None
        self._lock = threading.RLock()

        self._recognizer = sr.Recognizer() if sr else None
        self._calibrated_at = 0.0

    # -----------------------------
    # Status helpers
    # -----------------------------
    def set_status_callback(self, cb: Optional[StatusCallback]) -> None:
        self._status_cb = cb

    def _status(self, text: str) -> None:
        try:
            if self._status_cb:
                self._status_cb(text)
        except Exception:
            # Status callback must never crash voice.
            pass

    # -----------------------------
    # Microphone selection
    # -----------------------------
    def _pick_microphone(self):
        if sr is None:
            return None
        try:
            if not self.cfg.mic_name:
                return sr.Microphone()
            names = sr.Microphone.list_microphone_names()
            wanted = self.cfg.mic_name.lower()
            for idx, name in enumerate(names):
                if wanted in (name or "").lower():
                    return sr.Microphone(device_index=idx)
            return sr.Microphone()
        except Exception:
            return None

    # -----------------------------
    # Calibration + recognition
    # -----------------------------
    def _maybe_calibrate(self, source) -> None:
        if not self._recognizer:
            return
        now = time.time()
        if (now - self._calibrated_at) < self.cfg.calibration_ttl_s:
            return
        try:
            self._recognizer.dynamic_energy_threshold = True
            self._recognizer.pause_threshold = 0.7
            self._recognizer.non_speaking_duration = 0.4
            self._recognizer.adjust_for_ambient_noise(source, duration=self.cfg.calibration_duration_s)
        finally:
            self._calibrated_at = now

    def _recognize(self, audio) -> str:
        if not self._recognizer:
            return ""
        try:
            return (self._recognizer.recognize_google(audio, language=self.cfg.stt_language) or "").strip()
        except Exception:
            return ""

    def _strip_wake_word(self, text: str) -> str:
        t = (text or "").strip()
        if not t:
            return ""
        if not self.cfg.wake_enabled or not self.cfg.wake_word:
            return t
        low = t.lower()
        if self.cfg.wake_word not in low:
            return ""
        idx = low.find(self.cfg.wake_word)
        after = t[idx + len(self.cfg.wake_word) :].lstrip(" ,.!?;:")
        return after.strip()

    # -----------------------------
    # Public APIs
    # -----------------------------
    def listen_once(self) -> str:
        """
        Listen once and return a lowercase string (or "" on failure).
        """
        if sr is None or self._recognizer is None:
            self._status("Idle")
            return ""

        with self._lock:
            mic = self._pick_microphone()
            if mic is None:
                self._status("Idle")
                return ""

            # Two attempts: the second is a bit more forgiving.
            attempts = [
                (self.cfg.timeout, self.cfg.phrase_time_limit),
                (max(self.cfg.timeout, 8), self.cfg.phrase_time_limit),
            ]

            for i, (timeout, phrase_limit) in enumerate(attempts):
                try:
                    self._status("Listening...")
                    with mic as source:
                        self._maybe_calibrate(source)
                        audio = self._recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)

                    self._status("Thinking...")
                    text = self._recognize(audio)
                    text = self._strip_wake_word(text)
                    return (text or "").lower().strip()

                except getattr(sr, "WaitTimeoutError", Exception):
                    if i == len(attempts) - 1:
                        self._status("Idle")
                        return ""
                    continue
                except getattr(sr, "UnknownValueError", Exception):
                    if i == len(attempts) - 1:
                        self._status("Idle")
                        return ""
                    continue
                except getattr(sr, "RequestError", Exception):
                    self._status("Idle")
                    return ""
                except OSError:
                    self._status("Idle")
                    return ""
                except Exception:
                    self._status("Idle")
                    return ""

    def speak(self, text: str) -> None:
        """
        Speak asynchronously (won't block UI).
        Falls back to console if pyttsx3 isn't available.
        """

        def _run():
            self._status("Speaking...")
            if pyttsx3 is None:
                print(f"[Assistant]: {text}")
                self._status("Idle")
                return
            try:
                engine = pyttsx3.init()
                rate = int(engine.getProperty("rate") or 180)
                engine.setProperty("rate", max(120, rate + self.cfg.tts_rate_delta))
                engine.say(text)
                engine.runAndWait()
            except Exception:
                print(f"[Assistant]: {text}")
            self._status("Idle")

        threading.Thread(target=_run, daemon=True).start()


def _demo() -> None:
    v = Voice()
    v.set_status_callback(lambda s: print(f"[status] {s}"))

    print("Say something...")
    text = v.listen_once()
    if not text:
        print("Heard nothing.")
        return
    print("You said:", text)
    v.speak(f"You said {text}")

    # Give the TTS thread a moment in this demo script.
    time.sleep(1.5)


if __name__ == "__main__":
    _demo()

