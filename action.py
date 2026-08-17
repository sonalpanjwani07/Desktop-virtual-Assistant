import datetime
import re
import speak
import webbrowser
import weather
import os
import urllib.parse
import urllib.request
import json
import random
import sqlite3
import subprocess
from collections import Counter
from pathlib import Path
from zoneinfo import ZoneInfo
try:
    import psutil
except Exception:
    psutil = None
try:
    import pyautogui
except Exception:
    pyautogui = None
import requests
try:
    from PIL import ImageGrab
except Exception:
    ImageGrab = None
try:
    import pint
except Exception:
    pint = None
try:
    import mysql.connector  # type: ignore
except Exception:
    mysql = None  # type: ignore

# Load .env file if present so MySQL credentials can be configured easily
try:
    from dotenv import load_dotenv
    _env_path = Path(__file__).resolve().parent / ".env"
    if _env_path.exists():
        load_dotenv(dotenv_path=_env_path)
    else:
        load_dotenv()  # also checks CWD
except Exception:
    pass  # python-dotenv is optional

MUSIC_FOLDER = r'D:\music'

ureg = pint.UnitRegistry() if pint else None

# Offline joke pools (random pick each time). English / Hinglish (Roman Urdu mix).
JOKES_ENGLISH = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "I told my Wi‑Fi we weren't connecting anymore — it said it needed space.",
    "Parallel lines have so much in common. It's a shame they'll never meet.",
    "Why did the scarecrow win an award? He was outstanding in his field.",
    "I'm reading a book on anti‑gravity. It's impossible to put down!",
    "Why don't eggs tell jokes? They'd crack each other up.",
    "My alarm clock and I had a fight — now we're not on speaking terms.",
    "I used to play piano by ear… turns out you should use your hands.",
    "Why did the math book look sad? Too many problems.",
    "I'm on a seafood diet: I see food, and I eat it.",
    "Why can't bicycles stand up alone? They're two‑tired.",
    "I asked my dog what's two minus two — he said nothing.",
    "I'd explain electricity… but it's shocking.",
    "Why did the cookie go to the doctor? It felt crumbly.",
    "I'm friends with every triangle — we're always so acute.",
    "Why did the golfer bring two pants? In case he got a hole in one.",
    "I'm learning swimming… sink or swim — mostly sink.",
    "My fridge runs… good thing I caught it before it escaped.",
    "Why don't skeletons fight each other? They don't have the guts.",
    "Why was the computer cold? It left its Windows open.",
    "I'm writing a book about glue — can't put it down either.",
    "They say curiosity killed the cat… good thing I'm not a cat.",
]

JOKES_HINGLISH = [
    # First rotation when user asks hinglish / jokes in urdu (then existing list continues).
    "Friend: Tu itna chup kyun hai? Me: Data save kar raha hoon 😏",
    "Me: Mujhe space chahiye. Friend: NASA join kar 😏",
    "Friend: Tu serious kab hoga? Me: Jab battery 1% pe hogi 😏",
    "What did one calculator say to another? CASIO 😏",
    "[Kaisi Ho?]",
    "What do you call a lady who drinks only one tea in a day? Jaswanti 😏 [Just one Tea!]",
    "Hiroshima went for a singing competition, but Hiroshima Nagasaki 😏 [Na Ga Saki!!]",
    "Teacher: homework kyun nahi laaye? Student: Sir… Wi‑Fi ne dhoka de diya, dil tut gaya.",
    "Mom: beta utho subah ho gayi. Me: Mom… ye subah Monday wali hai ya Sunday wali?",
    "Friend: tu bahut lazy hai. Me: nahi yaar… energy‑saving mode pe hoon.",
    "Crush ne reply diya 'hmm'. Matlab science me pass, feelings me fail.",
    "Papa: marks kam aaye? Me: Papa… competition zyada tha, talent kam nahi.",
    "Exam me sab cheat kar rahe the… maine sirf window seat par scenery dekhi.",
    "Ghar wale: shaadi kab karoge? Me: pehle internet stable ho jaye.",
    "Dost: party kab dega? Me: jab bank balance party mood me ho jaye.",
    "Relative: kitna lamba ho gaya! Me: haan… bas salary short hai.",
    "Mom: phone chhod ke padhai karo. Phone: main hi to future hoon, Madam.",
    "Friend: tu serious kyun hai? Me: bro… Monday hai, smile budget khatam.",
    "Auto wala: meter se jana hai? Me: nahi bhai… dil se jana hai (discount ke saath).",
    "Exam hall me pen khatam… confidence bhi khatam… bas seating strong thi.",
    "Biwi ne kaha khana garam kar lo. Maine Wi‑Fi router ke paas rakh diya — smart husband.",
    "Boss: deadline kahan hai? Me: sir… wo calendar ke peeche chhupi hui hai.",
    "Diet start tomorrow — ye kal se wala programme 5 saal se chal raha hai.",
    "Friend: mood off hai. Me: recharge kara de… chai se.",
    "Neighbor: shor mat karo. Me: sorry uncle… ye hasi subscription free hai.",
    "Railway station pe announcement: train late… passenger ka patience early.",
    "Relative: padhai ka kya hua? Me: uncle… Netflix pe documentary dekh raha hoon — indirect study.",
    "Gym join kiya… membership full, motivation zero — perfect balance.",
    "Delivery: order late hua. Me: koi baat nahi… life bhi to late samajh me aati hai.",
]

# Real‑life fun facts (health, habits, brain, daily life).
FUNFACTS_REAL = [
    "Walking just 10 minutes after a meal can help blood sugar stay steadier — easy win.",
    "Your brain uses roughly 20% of your body's calories even when you're resting.",
    "Drinking water before coffee can reduce that jittery feeling for some people.",
    "Blue light at night can delay melatonin — dim screens an hour before bed helps sleep.",
    "Chewing gum while studying then chewing the same flavor during a test can jog memory.",
    "Writing tasks by hand often sticks better than typing for many learners.",
    "Cold showers (brief) can boost alertness — not magic, but a real jolt.",
    "Social media 'quick checks' often expand into 20+ minutes — timers really help.",
    "Meal prep on Sunday saves more weekday willpower than people expect.",
    "Deep breathing for one minute can lower heart rate before a stressful email.",
    "Labeling anxiety ('I'm nervous') can reduce its intensity a little — naming helps.",
    "Sunlight in the morning helps set your body clock for better night sleep.",
    "Small snacks with protein can reduce afternoon crashes better than sugar alone.",
    "Background TV lowers reading comprehension more than people admit.",
    "Multitasking often means slower work and more mistakes — batch similar tasks instead.",
    "Savings auto-transfer on payday beats relying on 'I'll save what's left'.",
    "Phone face-down on the desk reduces pick-ups for many people — simple hack.",
    "Gratitude lists don't fix everything but reliably nudge mood up a bit.",
    "Earbuds too loud for years can harm hearing — 60% volume rule is a good habit.",
    "Stretching hips and hamstrings can ease lower-back stiffness from sitting.",
    "Caffeine has a half-life of hours — afternoon coffee can still steal sleep.",
    "Making your bed is a tiny win that starts the day with completed task momentum.",
    "Replying to messages in batches reduces context-switch stress vs constant pings.",
    "Room a bit cool (not freezing) often supports deeper sleep than a warm room.",
    "Forgotten passwords cost global productivity absurd amounts — a password manager pays off.",
    "Kids copy stress cues — calmer reactions from adults actually regulate their nervous system.",
    "Micro-breaks every 45–60 minutes can sustain focus longer than grinding nonstop.",
    "Laughter triggers endorphins — even forced smiles can slightly lift mood.",
]


def _assistant_screenshot_dir():
    """
    Save screenshots in a real user folder, not the random process cwd.
    Tries: ~/Pictures/AssistantScreenshots, then ~/Desktop/AssistantScreenshots, then ./AssistantScreenshots.
    """
    for parent in (Path.home() / "Pictures", Path.home() / "Desktop", Path.cwd()):
        d = parent / "AssistantScreenshots"
        try:
            d.mkdir(parents=True, exist_ok=True)
            return d.resolve()
        except Exception:
            continue
    return Path.cwd().resolve()


def _capture_screenshot_file(file_path):
    # Primary method: pyautogui. Fallback: PIL ImageGrab.
    path = Path(file_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    target = str(path.resolve())
    try:
        if pyautogui is not None:
            screenshot = pyautogui.screenshot()
            screenshot.save(target)
            return os.path.isfile(target)
        if ImageGrab is not None:
            screenshot = ImageGrab.grab()
            screenshot.save(target)
            return os.path.isfile(target)
    except Exception:
        return False
    return False


def _assistant_data_dir():
    """Notes & reminders live here (not project folder): ~/Documents/AssistantData."""
    d = Path.home() / "Documents" / "AssistantData"
    try:
        d.mkdir(parents=True, exist_ok=True)
    except Exception:
        pass
    return d.resolve()


# First N hinglish jokes (jokes in urdu / hinglish joke) in order; then random from the rest of JOKES_HINGLISH.
HINGLISH_JOKE_PRIORITY = 7


def _next_hinglish_joke_line():
    """Return next pun from the priority block in order, then random from remaining list."""
    pool = JOKES_HINGLISH
    if len(pool) <= HINGLISH_JOKE_PRIORITY:
        return random.choice(pool)
    state = _assistant_data_dir() / "hinglish_joke_seq.txt"
    try:
        n = int(state.read_text(encoding="utf-8").strip() or "0")
    except Exception:
        n = 0
    if n < HINGLISH_JOKE_PRIORITY:
        line = pool[n]
        try:
            state.write_text(str(n + 1), encoding="utf-8")
        except Exception:
            pass
        return line
    return random.choice(pool[HINGLISH_JOKE_PRIORITY:])


# --- Text summarization (paragraph + "summarize" / "concise" / "make it short") ---
_SUMMARIZE_TRIGGERS = (
    "summarize this",
    "summarise this",
    "summarize the following",
    "summarise the following",
    "make it short",
    "make this short",
    "make it concise",
    "make this concise",
    "concise it",
    "make it shorter",
    "make this shorter",
    "shorten this",
    "shorten it",
    "brief version",
    "in short",
    "tl;dr",
    "tldr",
    "summarize",
    "summarise",
    "summary of",
    "summary",
    "concise",
    "brief",
    "please summarize",
    "please summarise",
    "give me a summary",
    "short version",
)

_SUMMARIZE_END_TRIGGERS = (
    "summarize it",
    "summarise it",
    "make it short",
    "make it concise",
    "concise it",
    "shorten it",
    "make it shorter",
    "please summarize",
    "please summarise",
    "in brief",
)

_STOP_WORDS = frozenset(
    "a an the and or but if is are was were be been being in on at to for of as by with from "
    "that this these those it its i you he she they we my your their our".split()
)


def _wants_summarize(lower_text: str) -> bool:
    t = (lower_text or "").strip()
    if not t:
        return False
    if any(p in t for p in _SUMMARIZE_TRIGGERS):
        return True
    # "make this concise" / "keep it brief" style
    return bool(re.search(r"\b(concise|brief|shorter|shorten|summar\w*)\b", t))


def _is_long_form_text(text: str) -> bool:
    """Multi-sentence paste — not a short voice command."""
    t = (text or "").strip()
    return len(t) > 100 or len(t.split()) > 18


def _is_explicit_web_search(lower_text: str) -> bool:
    """True only for short, explicit search commands — not paragraphs."""
    if _wants_summarize(lower_text) or _is_long_form_text(lower_text):
        return False
    t = (lower_text or "").strip()
    if not t:
        return False
    if not re.search(r"\bsearch\b", t):
        return False
    # Must look like a command, not an essay mentioning "search"
    if t.startswith("search ") or t.startswith("search:"):
        return True
    if len(t) < 70 and re.search(r"^search\b", t):
        return True
    return len(t.split()) <= 8 and "search" in t.split()[:2]


def _extract_text_for_summary(original: str, lower_text: str) -> str:
    """Pull paragraph body out of commands like 'summarize: ...' or '... please summarize it'."""
    original = (original or "").strip()
    lower_text = (lower_text or "").strip()
    if not original:
        return ""

    for end_phrase in _SUMMARIZE_END_TRIGGERS:
        if lower_text.endswith(end_phrase):
            body = original[: len(original) - len(end_phrase)].strip(" .,;:-\n\t")
            if len(body) >= 30:
                return body

    for phrase in sorted(_SUMMARIZE_TRIGGERS, key=len, reverse=True):
        if lower_text.startswith(phrase):
            body = original[len(phrase) :].strip(" :;,-\n\t")
            if len(body) >= 30:
                return body

    body = original
    for phrase in sorted(_SUMMARIZE_TRIGGERS, key=len, reverse=True):
        body = re.sub(re.escape(phrase), "", body, flags=re.IGNORECASE)
    body = body.strip(" :;,-\n\t")
    if len(body) >= 25:
        return body
    # Long paste with a summarize keyword anywhere — use full text minus triggers
    if len(original) >= 80 and _wants_summarize(lower_text):
        return body if len(body) >= 25 else original
    return ""


def _summarize_extractive(text: str, max_sentences: int = 4) -> str:
    """Offline summary: pick the most informative sentences."""
    text = re.sub(r"\s+", " ", (text or "").strip())
    if not text:
        return ""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(sentences) <= 1:
        words = text.split()
        if len(words) <= 40:
            return text
        return " ".join(words[:40]) + "..."
    if len(sentences) <= max_sentences:
        return text

    words = re.findall(r"[a-zA-Z']{3,}", text.lower())
    freq = Counter(w for w in words if w not in _STOP_WORDS)

    def score(sentence: str) -> int:
        return sum(freq.get(w.lower(), 0) for w in re.findall(r"[a-zA-Z']+", sentence))

    top = sorted(sentences, key=score, reverse=True)[:max_sentences]
    top_set = set(top)
    ordered = [s for s in sentences if s in top_set]
    return " ".join(ordered)


def _summarize_with_openai(text: str) -> str:
    """Optional better summary when OPENAI_API_KEY is set."""
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or requests is None:
        return ""
    try:
        resp = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "model": os.getenv("OPENAI_SUMMARY_MODEL", "gpt-4o-mini"),
                "messages": [
                    {
                        "role": "system",
                        "content": (
                            "You summarize text clearly in English. "
                            "Return only the concise summary in 2-5 sentences. No preamble."
                        ),
                    },
                    {"role": "user", "content": text[:12000]},
                ],
                "temperature": 0.3,
                "max_tokens": 400,
            },
            timeout=45,
        )
        if resp.status_code != 200:
            return ""
        data = resp.json()
        return (data.get("choices", [{}])[0].get("message", {}).get("content") or "").strip()
    except Exception:
        return ""


def summarize_paragraph(text: str) -> str:
    """Public helper: concise summary (API if available, else extractive)."""
    text = (text or "").strip()
    if not text:
        return "Please paste a paragraph to summarize."
    if len(text) < 30:
        return "That text is too short to summarize. Add a longer paragraph."

    ai = _summarize_with_openai(text)
    if ai:
        return ai
    return _summarize_extractive(text)


class DatabaseManager:
    """Dual backend logger: MySQL (preferred) + SQLite fallback."""

    def __init__(self, db_path="smart_ai_assistant_pro.db"):
        self.db_path = db_path
        self.mysql_enabled = False
        self.mysql_last_error = ""
        self.mysql_config = {
            "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
            "port": int(os.getenv("MYSQL_PORT", "3306")),
            "user": (
                os.getenv("MYSQL_USER")
                or os.getenv("MYSQL_USERNAME")
                or "root"
            ),
            "password": (
                os.getenv("MYSQL_PASSWORD")
                or os.getenv("MYSQL_PASS")
                or os.getenv("MYSQL_ROOT_PASSWORD")
                or ""
            ),
            "database": "log",
        }
        self._create_tables()
        self._setup_mysql()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _create_tables(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS mood_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    mood TEXT NOT NULL,
                    suggestion TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    command TEXT NOT NULL,
                    input_text TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS funfact_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fact TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def _setup_mysql(self):
        if "mysql" not in globals() or mysql is None:
            return
        try:
            root_conn = mysql.connector.connect(
                host=self.mysql_config["host"],
                port=self.mysql_config["port"],
                user=self.mysql_config["user"],
                password=self.mysql_config["password"],
            )
            root_cur = root_conn.cursor()
            root_cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{self.mysql_config['database']}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
            root_conn.commit()
            root_cur.close()
            root_conn.close()

            conn = mysql.connector.connect(**self.mysql_config)
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(120) NOT NULL UNIQUE,
                    created_at DATETIME NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS command_types (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    command_name VARCHAR(100) NOT NULL UNIQUE,
                    created_at DATETIME NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    command_type_id INT NOT NULL,
                    input_text TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (command_type_id) REFERENCES command_types(id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS user_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    command VARCHAR(100) NOT NULL,
                    input_text TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS mood_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    mood VARCHAR(50) NOT NULL,
                    suggestion TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS funfact_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    fact TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS app_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    app_name VARCHAR(120) NOT NULL,
                    status_message TEXT NOT NULL,
                    timestamp DATETIME NOT NULL
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS search_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    activity_log_id INT NULL,
                    query_text TEXT NOT NULL,
                    search_engine VARCHAR(40) NOT NULL,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (activity_log_id) REFERENCES activity_logs(id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS weather_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    activity_log_id INT NULL,
                    city VARCHAR(120) NOT NULL,
                    country VARCHAR(80) NULL,
                    channel VARCHAR(80) NULL,
                    temperature_c DECIMAL(6,2) NULL,
                    feels_like_c DECIMAL(6,2) NULL,
                    weather_description VARCHAR(255) NULL,
                    result_text TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (activity_log_id) REFERENCES activity_logs(id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS gift_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    activity_log_id INT NULL,
                    occasion VARCHAR(50) NOT NULL,
                    relation_name VARCHAR(50) NOT NULL,
                    suggestions TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (activity_log_id) REFERENCES activity_logs(id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS file_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    activity_log_id INT NULL,
                    query_text TEXT NOT NULL,
                    match_path TEXT,
                    action_type VARCHAR(30) NOT NULL,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (activity_log_id) REFERENCES activity_logs(id)
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS screenshot_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    activity_log_id INT NULL,
                    file_path TEXT NOT NULL,
                    timestamp DATETIME NOT NULL,
                    FOREIGN KEY (activity_log_id) REFERENCES activity_logs(id)
                )
                """
            )
            self._migrate_mysql_schema(cur)
            conn.commit()
            cur.close()
            conn.close()
            self.mysql_enabled = True
            self.mysql_last_error = ""
            self._ensure_seed_data()
        except Exception as exc:
            self.mysql_enabled = False
            self.mysql_last_error = str(exc)

    def _column_exists(self, cur, table_name, column_name):
        cur.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
            """,
            (self.mysql_config["database"], table_name, column_name),
        )
        row = cur.fetchone()
        return bool(row and row[0] > 0)

    def _migrate_mysql_schema(self, cur):
        # Upgrade old tables in-place without breaking existing data.
        try:
            if not self._column_exists(cur, "search_logs", "activity_log_id"):
                cur.execute("ALTER TABLE search_logs ADD COLUMN activity_log_id INT NULL")
            if not self._column_exists(cur, "weather_logs", "activity_log_id"):
                cur.execute("ALTER TABLE weather_logs ADD COLUMN activity_log_id INT NULL")
            if not self._column_exists(cur, "weather_logs", "country"):
                cur.execute("ALTER TABLE weather_logs ADD COLUMN country VARCHAR(80) NULL")
            if not self._column_exists(cur, "weather_logs", "channel"):
                cur.execute("ALTER TABLE weather_logs ADD COLUMN channel VARCHAR(80) NULL")
            if not self._column_exists(cur, "weather_logs", "temperature_c"):
                cur.execute("ALTER TABLE weather_logs ADD COLUMN temperature_c DECIMAL(6,2) NULL")
            if not self._column_exists(cur, "weather_logs", "feels_like_c"):
                cur.execute("ALTER TABLE weather_logs ADD COLUMN feels_like_c DECIMAL(6,2) NULL")
            if not self._column_exists(cur, "weather_logs", "weather_description"):
                cur.execute("ALTER TABLE weather_logs ADD COLUMN weather_description VARCHAR(255) NULL")
            if not self._column_exists(cur, "gift_logs", "activity_log_id"):
                cur.execute("ALTER TABLE gift_logs ADD COLUMN activity_log_id INT NULL")
            if not self._column_exists(cur, "file_logs", "activity_log_id"):
                cur.execute("ALTER TABLE file_logs ADD COLUMN activity_log_id INT NULL")
            if not self._column_exists(cur, "screenshot_logs", "activity_log_id"):
                cur.execute("ALTER TABLE screenshot_logs ADD COLUMN activity_log_id INT NULL")
        except Exception:
            pass

    def get_mysql_status(self):
        """Return a human-readable string describing the current MySQL connection status."""
        if "mysql" not in globals() or mysql is None:
            return (
                "MySQL: mysql-connector-python is not installed.\n"
                "Run: pip install mysql-connector-python\n"
                "Logging to SQLite only."
            )
        if self.mysql_enabled:
            cfg = self.mysql_config
            return (
                f"MySQL: connected  host={cfg['host']}  port={cfg['port']}  "
                f"user={cfg['user']}  database={cfg['database']}"
            )
        hint = (
            "Set credentials in a .env file next to action.py:\n"
            "  MYSQL_HOST=127.0.0.1\n"
            "  MYSQL_PORT=3306\n"
            "  MYSQL_USER=root\n"
            "  MYSQL_PASSWORD=your_password\n"
            "Make sure MySQL / MySQL Workbench server is running."
        )
        return (
            f"MySQL: not connected\n"
            f"Error: {self.mysql_last_error or 'unknown'}\n\n"
            f"{hint}\n"
            f"Falling back to SQLite."
        )

    def _mysql_connect(self):
        if not self.mysql_enabled:
            self._setup_mysql()
        if not self.mysql_enabled:
            return None
        try:
            return mysql.connector.connect(**self.mysql_config)
        except Exception as exc:
            self.mysql_enabled = False
            self.mysql_last_error = str(exc)
            return None

    def _ensure_seed_data(self):
        try:
            conn = self._mysql_connect()
            if not conn:
                return
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users(username, created_at) VALUES (%s, %s) ON DUPLICATE KEY UPDATE username = username",
                ("default_user", self._now()),
            )
            conn.commit()
            cur.close()
            conn.close()
        except Exception:
            pass

    def _get_default_user_id(self):
        try:
            conn = self._mysql_connect()
            if not conn:
                return None
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE username = %s LIMIT 1", ("default_user",))
            row = cur.fetchone()
            cur.close()
            conn.close()
            return row[0] if row else None
        except Exception:
            return None

    def _get_or_create_command_type_id(self, command):
        try:
            conn = self._mysql_connect()
            if not conn:
                return None
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO command_types(command_name, created_at) VALUES (%s, %s) ON DUPLICATE KEY UPDATE command_name = command_name",
                (command, self._now()),
            )
            conn.commit()
            cur.execute("SELECT id FROM command_types WHERE command_name = %s LIMIT 1", (command,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            return row[0] if row else None
        except Exception:
            return None

    def _log_activity(self, command, input_text):
        if not self.mysql_enabled:
            return None
        user_id = self._get_default_user_id()
        command_id = self._get_or_create_command_type_id(command or "unknown")
        if not user_id or not command_id:
            return None
        try:
            conn = self._mysql_connect()
            if not conn:
                return None
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO activity_logs(user_id, command_type_id, input_text, timestamp) VALUES (%s, %s, %s, %s)",
                (user_id, command_id, input_text, self._now()),
            )
            conn.commit()
            activity_id = cur.lastrowid
            cur.close()
            conn.close()
            return activity_id
        except Exception:
            return None

    def _now(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def log_user_action(self, command, input_text):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO user_history(command, input_text, timestamp) VALUES (?, ?, ?)",
                (command, input_text, self._now()),
            )
            conn.commit()
        conn = self._mysql_connect()
        if conn:
            try:
                cur = conn.cursor()
                self._log_activity(command, input_text)
                cur.execute(
                    "INSERT INTO user_history(command, input_text, timestamp) VALUES (%s, %s, %s)",
                    (command, input_text, self._now()),
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as exc:
                self.mysql_last_error = str(exc)
                pass

    def get_last_mood_suggestion(self, mood):
        with self._connect() as conn:
            row = conn.execute(
                "SELECT suggestion FROM mood_logs WHERE mood=? ORDER BY id DESC LIMIT 1",
                (mood,),
            ).fetchone()
            return row[0] if row else None

    def log_mood(self, mood, suggestion):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO mood_logs(mood, suggestion, timestamp) VALUES (?, ?, ?)",
                (mood, suggestion, self._now()),
            )
            conn.commit()
        conn = self._mysql_connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO mood_logs(mood, suggestion, timestamp) VALUES (%s, %s, %s)",
                    (mood, suggestion, self._now()),
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as exc:
                self.mysql_last_error = str(exc)
                pass

    def get_last_funfact(self):
        with self._connect() as conn:
            row = conn.execute("SELECT fact FROM funfact_logs ORDER BY id DESC LIMIT 1").fetchone()
            return row[0] if row else None

    def log_funfact(self, fact):
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO funfact_logs(fact, timestamp) VALUES (?, ?)",
                (fact, self._now()),
            )
            conn.commit()
        conn = self._mysql_connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO funfact_logs(fact, timestamp) VALUES (%s, %s)",
                    (fact, self._now()),
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as exc:
                self.mysql_last_error = str(exc)
                pass

    def log_search(self, query_text, search_engine, activity_log_id=None):
        conn = self._mysql_connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO search_logs(activity_log_id, query_text, search_engine, timestamp) VALUES (%s, %s, %s, %s)",
                    (activity_log_id, query_text, search_engine, self._now()),
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as exc:
                self.mysql_last_error = str(exc)
                pass

    def log_app(self, app_name, status_message):
        conn = self._mysql_connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO app_logs(app_name, status_message, timestamp) VALUES (%s, %s, %s)",
                    (app_name, status_message, self._now()),
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as exc:
                self.mysql_last_error = str(exc)
                pass

    def log_weather(
        self,
        city,
        result_text,
        country=None,
        channel=None,
        temperature_c=None,
        feels_like_c=None,
        weather_description=None,
        activity_log_id=None,
    ):
        conn = self._mysql_connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO weather_logs(
                        activity_log_id, city, country, channel, temperature_c,
                        feels_like_c, weather_description, result_text, timestamp
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        activity_log_id,
                        city,
                        country,
                        channel,
                        temperature_c,
                        feels_like_c,
                        weather_description,
                        result_text,
                        self._now(),
                    ),
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as exc:
                self.mysql_last_error = str(exc)
                pass

    def log_gift(self, occasion, relation_name, suggestions):
        conn = self._mysql_connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO gift_logs(occasion, relation_name, suggestions, timestamp) VALUES (%s, %s, %s, %s)",
                    (occasion, relation_name, suggestions, self._now()),
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as exc:
                self.mysql_last_error = str(exc)
                pass

    def log_file(self, query_text, match_path, action_type):
        conn = self._mysql_connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO file_logs(query_text, match_path, action_type, timestamp) VALUES (%s, %s, %s, %s)",
                    (query_text, match_path, action_type, self._now()),
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as exc:
                self.mysql_last_error = str(exc)
                pass

    def log_screenshot(self, file_path):
        conn = self._mysql_connect()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO screenshot_logs(file_path, timestamp) VALUES (%s, %s)",
                    (file_path, self._now()),
                )
                conn.commit()
                cur.close()
                conn.close()
            except Exception as exc:
                self.mysql_last_error = str(exc)
                pass


class SmartFeatureHandler:
    """New smart commands while keeping legacy handlers intact."""

    def __init__(self, db):
        self.db = db
        self.moods = {
            "sad": [
                "Take a short walk and breathe deeply.",
                "Listen to one uplifting song.",
                "Write 3 things you are grateful for.",
                "Drink water and stretch for 2 minutes.",
                "Talk to a trusted friend for support.",
                "Watch a short comedy clip.",
                "Complete one tiny task for momentum.",
                "Sit in sunlight for a few minutes.",
            ],
            "happy": [
                "Capture this moment in a journal.",
                "Share your joy with someone close.",
                "Use this energy to finish one key task.",
                "Take a memory photo of this moment.",
                "List 5 things you appreciate today.",
                "Celebrate with a healthy reward.",
                "Play your favorite playlist.",
                "Set one exciting goal for today.",
            ],
            "excited": [
                "Write your idea before you forget details.",
                "Start with the highest-impact step first.",
                "Break the plan into 3 quick actions.",
                "Use a 25-minute focus sprint.",
                "Share your idea for feedback.",
                "Stay hydrated and pace your energy.",
                "Track progress after each small win.",
                "Turn excitement into a clear checklist.",
            ],
            "anxious": [
                "Try 4-4-4 breathing for one minute.",
                "List what is in your control right now.",
                "Avoid social media for 30 minutes.",
                "Do a grounding exercise around you.",
                "Take a short walk to reset.",
                "Write one worry and one next action.",
                "Drink warm water and pause.",
                "Start with one very small task.",
            ],
            "upset": [
                "Pause before reacting and breathe slowly.",
                "Write what happened and how you feel.",
                "Take a 10-minute reset break.",
                "Move physically to release stress.",
                "Talk to someone calm and supportive.",
                "Focus on facts over assumptions.",
                "Do one calming activity now.",
                "Return once your mind is clearer.",
            ],
            "pathetic": [
                "This feeling is temporary; be kind to yourself.",
                "Take a shower and reset your day.",
                "Do one basic self-care action now.",
                "Complete one small achievable task.",
                "Go outside for fresh air.",
                "Write one thing you still did well.",
                "Rest briefly, then restart small.",
                "Talk to yourself like a good friend.",
            ],
        }
        self.funfacts = FUNFACTS_REAL
        self.jokes_english = JOKES_ENGLISH
        self.jokes_hinglish = JOKES_HINGLISH
        self.app_commands = {
            "vscode": ["code"],
            "chrome": ["cmd", "/c", "start", "chrome"],
            "notepad": ["notepad"],
            "mysql": ["cmd", "/c", "start", "mysqlworkbench"],
        }
        self.gift_ideas = {
            "eid": ["customized prayer mat", "premium perfume set", "family photo frame", "handwritten gratitude card", "wellness gift hamper"],
            "holi": ["organic colors hamper", "festival sweets box", "traditional wear gift card", "home decor lights", "artistic rangoli kit"],
            "birthday": ["personalized memory scrapbook", "smart desk organizer", "custom name pendant", "experience voucher", "book + note set"],
            "diwali": ["handcrafted diya set", "luxury sweets and nuts", "decorative lantern combo", "aroma candle hamper", "festive clothing voucher"],
        }
        self.relations = {"mother", "father", "sister", "brother", "friend"}
        self._weather_channels = {"geo", "ary", "samaa", "dawn", "bbc", "cnn", "sky"}

    def _open_app(self, name):
        app_aliases = {
            "vs code": "vscode",
            "visual studio code": "vscode",
            "workbench": "mysql",
            "mysql workbench": "mysql",
        }
        name = app_aliases.get(name, name)
        cmd = self.app_commands.get(name)
        generic_cmd = ["cmd", "/c", "start", "", name]
        if not cmd:
            cmd = generic_cmd
        try:
            subprocess.Popen(cmd, shell=False)
            return f"Opening {name}..."
        except FileNotFoundError:
            try:
                subprocess.Popen(generic_cmd, shell=False)
                return f"Trying to open {name}..."
            except Exception:
                return f"{name} command not found. Please configure installed path."
        except Exception as exc:
            return f"Unable to open {name}: {exc}"

    @staticmethod
    def _extract_phrase_after(text, token):
        idx = text.find(token)
        if idx == -1:
            return ""
        return text[idx + len(token) :].strip()

    def _find_in_common_locations(self, query):
        roots = [
            Path.cwd(),
            Path.home() / "Desktop",
            Path.home() / "Documents",
            Path.home() / "Downloads",
        ]
        q = query.lower().strip()
        for root in roots:
            if not root.exists():
                continue
            try:
                for path in root.rglob("*"):
                    name = path.name.lower()
                    if q in name:
                        return str(path)
            except Exception:
                continue
        return None

    def _parse_weather_input(self, raw_value):
        raw_text = (raw_value or "").strip()
        if not raw_text:
            return {"city": "Karachi", "country": "", "channel": ""}
        normalized = raw_text.replace("|", ",")
        parts = [p.strip() for p in normalized.split(",") if p.strip()]
        if len(parts) >= 3:
            return {"city": parts[0], "country": parts[1], "channel": parts[2]}
        if len(parts) == 2:
            return {"city": parts[0], "country": parts[1], "channel": ""}
        words = raw_text.split()
        if len(words) >= 2 and words[-1].lower() in self._weather_channels:
            return {"city": " ".join(words[:-1]), "country": "", "channel": words[-1]}
        return {"city": raw_text, "country": "", "channel": ""}

    def _weather(self, city, country="", channel=""):
        city = city.strip() if city else "Karachi"
        country = (country or "").strip()
        channel = (channel or "").strip()
        api_key = (
            os.getenv("OPENWEATHER_API_KEY", "").strip()
            or os.getenv("OPENWEATHERMAP_API_KEY", "").strip()
            or os.getenv("ASSISTANT_WEATHER_API_KEY", "").strip()
        )
        if not api_key:
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote_plus('weather in ' + city)}")
            return {
                "result_text": f"Opened weather search for {city}.",
                "temperature_c": None,
                "feels_like_c": None,
                "weather_description": None,
            }
        try:
            weather_query = f"{city},{country}" if country else city
            params = urllib.parse.urlencode({"q": weather_query, "appid": api_key, "units": "metric"})
            with urllib.request.urlopen(f"https://api.openweathermap.org/data/2.5/weather?{params}", timeout=8) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            desc = payload.get("weather", [{}])[0].get("description", "N/A")
            temp = payload.get("main", {}).get("temp", "N/A")
            feels = payload.get("main", {}).get("feels_like", "N/A")
            source_note = f" via {channel}" if channel else ""
            return {
                "result_text": f"Weather in {city}{', ' + country if country else ''}{source_note}: {desc}, temp {temp} C, feels like {feels} C.",
                "temperature_c": temp if isinstance(temp, (int, float)) else None,
                "feels_like_c": feels if isinstance(feels, (int, float)) else None,
                "weather_description": desc,
            }
        except Exception:
            webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote_plus('weather in ' + city)}")
            return {
                "result_text": f"Could not fetch API weather. Opened weather search for {city}.",
                "temperature_c": None,
                "feels_like_c": None,
                "weather_description": None,
            }

    def handle(self, data_btn):
        text = (data_btn or "").strip()
        if not text:
            return None
        lower_text = text.lower()
        tokens = set(lower_text.split())
        parts = text.split()
        main_cmd = parts[0] if parts else ""
        try:
            self.db.log_user_action(main_cmd, text)
        except Exception:
            pass

        # Let SummarizeHandler run first (do not treat long text as search/open).
        if _wants_summarize(lower_text):
            return None

        # Do not treat long pasted paragraphs as open/search/play commands.
        if _is_long_form_text(lower_text):
            return None

        if "mood" in tokens:
            mood = ""
            for candidate in self.moods.keys():
                if candidate in lower_text:
                    mood = candidate
                    break
            if mood not in self.moods:
                return "Unknown mood. Try: sad, happy, excited, anxious, upset, pathetic."
            last = self.db.get_last_mood_suggestion(mood)
            options = [s for s in self.moods[mood] if s != last]
            suggestion = random.choice(options if options else self.moods[mood])
            self.db.log_mood(mood, suggestion)
            speak.speak(suggestion)
            return suggestion

        if "screenshot" in lower_text or "capture screen" in lower_text or "screen shot" in lower_text:
            try:
                stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                file_name = f"screenshot_{stamp}.png"
                save_dir = _assistant_screenshot_dir()
                file_path = str((save_dir / file_name).resolve())
                if not _capture_screenshot_file(file_path):
                    return "Screenshot dependency missing. Install pyautogui or pillow."
                self.db.log_screenshot(file_path)
                try:
                    os.startfile(file_path)
                except Exception:
                    try:
                        os.startfile(str(save_dir))
                    except Exception:
                        pass
                result = f"Screenshot saved: {file_path}"
                speak.speak(result)
                return result
            except Exception:
                return "Screenshot failed."

        if "open" in tokens:
            app_name = self._extract_phrase_after(lower_text, "open")
            if not app_name:
                return "Tell me what to open."
            # If user asked to open a file/folder/doc, try file discovery first.
            if any(k in lower_text for k in ["file", "folder", "doc", "document"]):
                path = self._find_in_common_locations(app_name.replace("file", "").replace("folder", "").replace("document", "").replace("doc", "").strip())
                if path:
                    try:
                        os.startfile(path)
                        self.db.log_file(app_name, path, "open")
                        result = f"Opened: {path}"
                        speak.speak("Opening your file")
                        return result
                    except Exception:
                        pass
            result = self._open_app(app_name)
            self.db.log_app(app_name, result)
            speak.speak(result)
            return result

        if _is_explicit_web_search(lower_text) or (
            "find" in tokens and any(k in lower_text for k in ["file", "folder", "doc", "document"])
        ):
            if _is_explicit_web_search(lower_text):
                query = re.sub(r"^\s*search\s*", "", lower_text, count=1, flags=re.I).strip()
            else:
                query = lower_text
            if query:
                if any(k in lower_text for k in ["file", "folder", "doc", "document", "local"]):
                    cleaned = (
                        query.replace("file", "")
                        .replace("folder", "")
                        .replace("document", "")
                        .replace("doc", "")
                        .replace("local", "")
                        .replace("find", "")
                        .strip()
                    )
                    found = self._find_in_common_locations(cleaned)
                    if found:
                        self.db.log_file(cleaned, found, "find")
                        result = f"Found: {found}"
                        speak.speak("Found one matching file.")
                        return result
                    self.db.log_file(cleaned, "", "find")
                    return "No matching file or folder found in common locations."
                webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}")
                result = f"Searching Google for {query}"
                self.db.log_search(query, "google")
                speak.speak(result)
                return result

        if "play" in tokens and "news" in tokens:
            channel_map = {"geo": "Geo News", "samaa": "Samaa News", "ary": "ARY News"}
            channel_key = next((c for c in channel_map if c in lower_text), None)
            channel_name = channel_map.get(channel_key, "Pakistan News")
            if "5 days before" in lower_text or "5 day" in lower_text:
                when = "5 days ago"
            elif "today" in lower_text:
                when = "today"
            elif "latest" in lower_text:
                when = "latest"
            else:
                when = ""
            query = f"{channel_name} {when} Pakistan".strip()
            webbrowser.open(
                "https://www.youtube.com/results?search_query=" + urllib.parse.quote_plus(query)
            )
            result = f"Playing news search: {query}"
            speak.speak(result)
            return result

        if "weather" in lower_text:
            weather_input = lower_text.split("weather", 1)[1].strip()
            parsed = self._parse_weather_input(weather_input)
            weather_data = self._weather(parsed["city"], parsed["country"], parsed["channel"])
            result = weather_data["result_text"]
            self.db.log_weather(
                parsed["city"],
                result,
                country=parsed["country"] or None,
                channel=parsed["channel"] or None,
                temperature_c=weather_data["temperature_c"],
                feels_like_c=weather_data["feels_like_c"],
                weather_description=weather_data["weather_description"],
            )
            speak.speak(result)
            return result

        if "funfact" in lower_text or "fun fact" in lower_text:
            last = self.db.get_last_funfact()
            options = [f for f in self.funfacts if f != last]
            fact = random.choice(options if options else self.funfacts)
            self.db.log_funfact(fact)
            speak.speak(fact)
            return fact

        # Jokes: Hinglish/Urdu-style first (e.g. "jokes in urdu", "hinglish joke", "desi joke"), then English pool.
        if "fun fact" not in lower_text:
            hinglish_joke = (
                ("hinglish" in lower_text and ("joke" in lower_text or "jokes" in lower_text))
                or "jokes in urdu" in lower_text
                or "joke in urdu" in lower_text
                or "urdu joke" in lower_text
                or "urdu jokes" in lower_text
                or "desi joke" in lower_text
                or "desi jokes" in lower_text
            )
            if hinglish_joke:
                joke_h = _next_hinglish_joke_line()
                speak.speak(joke_h)
                return joke_h
            if "joke" in lower_text or "jokes" in lower_text:
                joke_e = random.choice(self.jokes_english)
                speak.speak(joke_e)
                return joke_e

        if "gift" in tokens:
            seg = lower_text.split()
            occasion = next((o for o in self.gift_ideas.keys() if o in seg), "")
            relation = next((r for r in self.relations if r in seg), "")
            if not occasion or not relation:
                return "Usage: gift <eid|holi|birthday|diwali> <mother|father|sister|brother|friend>"
            if occasion not in self.gift_ideas:
                return "Unknown occasion. Try: eid, holi, birthday, diwali."
            if relation not in self.relations:
                return "Unknown relation. Try: mother, father, sister, brother, friend."
            picks = random.sample(self.gift_ideas[occasion], k=4)
            result = f"Gift ideas for {relation} on {occasion}: " + "; ".join(picks)
            self.db.log_gift(occasion, relation, "; ".join(picks))
            speak.speak(result)
            return result

        return None


def _find_song(song_name, songs):
    song_name = song_name.lower().strip()
    for song in songs:
        if song_name in song.lower():
            return song
    return None


def _is_generic_spotify_request(song_name):
    normalized = song_name.lower()
    for token in ['on spotify', 'spotify', 'play', 'play song', 'play the song', 'song', 'music', 'songs', 'my music', 'my song']:
        normalized = normalized.replace(token, '')
    normalized = normalized.strip()
    return not normalized


def _extract_url(text):
    match = re.search(r'(https?://\S+)', text, re.IGNORECASE)
    if match:
        return match.group(1).rstrip('.,!?')
    if 'spotify.com/' in text.lower():
        link_part = text[text.lower().index('spotify.com/') :].split()[0].rstrip('.,!?')
        return 'https://' + link_part
    if 'open.spotify.com' in text.lower():
        link_part = text[text.lower().index('open.spotify.com') :].split()[0].rstrip('.,!?')
        return 'https://' + link_part
    return None


class GreetingHandler:
    def handle(self, data_btn):
        if "what is your name" in data_btn:
            speak.speak("my name is virtual Assistant")
            return "my name is virtual Assistant"
        elif "hello" in data_btn or "hye" in data_btn or "hay" in data_btn:
            speak.speak("Hey sir, How i can help you !")
            return "Hey sir, How i can help you !"
        elif "how are you" in data_btn:
            speak.speak("I am doing great these days sir")
            return "I am doing great these days sir"
        elif "thanku" in data_btn or "thank" in data_btn:
            speak.speak("its my pleasure sir to stay with you")
            return "its my pleasure sir to stay with you"
        elif "good morning" in data_btn:
            speak.speak("Good morning sir, i think you might need some help")
            return "Good morning sir, i think you might need some help"
        return None


class TimeHandler:
    def handle(self, data_btn):
        timezone_map = {
            "pakistan": "Asia/Karachi",
            "india": "Asia/Kolkata",
            "uae": "Asia/Dubai",
            "dubai": "Asia/Dubai",
            "saudi": "Asia/Riyadh",
            "uk": "Europe/London",
            "london": "Europe/London",
            "usa": "America/New_York",
            "us": "America/New_York",
            "new york": "America/New_York",
            "canada": "America/Toronto",
            "australia": "Australia/Sydney",
            "japan": "Asia/Tokyo",
            "china": "Asia/Shanghai",
            "germany": "Europe/Berlin",
            "france": "Europe/Paris",
        }
        if "time now" in data_btn or "right now" in data_btn or data_btn.strip() == "time":
            current_time = datetime.datetime.now()
            Time = f"Right now local time is {current_time.strftime('%I:%M %p')}"
            speak.speak(Time)
            return Time
        elif "time in" in data_btn:
            place = data_btn.split("time in", 1)[1].strip()
            tz_name = ""
            for key, value in timezone_map.items():
                if key in place:
                    tz_name = value
                    break
            if not tz_name:
                return "Please say: time in <country>, for example time in pakistan."
            try:
                now_tz = datetime.datetime.now(ZoneInfo(tz_name))
                result = f"Current time in {place.title()} is {now_tz.strftime('%I:%M %p')}"
                speak.speak(result)
                return result
            except Exception:
                return "Unable to fetch that country's time."
        elif "shutdown" in data_btn or "quit" in data_btn:
            speak.speak("ok sir")
            return "ok sir"
        return None


class MusicHandler:
    def handle(self, data_btn):
        if 'play music from my laptop' in data_btn or 'music from my laptop' in data_btn:
            try:
                songs = os.listdir(MUSIC_FOLDER)
                if songs:
                    os.startfile(os.path.join(MUSIC_FOLDER, songs[0]))
                    speak.speak("Songs playing from your music folder")
                    return "Songs playing from your music folder"
                else:
                    speak.speak("No songs found in the music folder")
                    return "No songs found in the music folder"
            except Exception:
                speak.speak("Music folder not found")
                return "Music folder not found"
        elif 'play' in data_btn:
            if 'spotify' in data_btn and 'on spotify' in data_btn:
                song_name = data_btn
                for prefix in ['play song', 'play the song', 'play ', 'song ']:
                    if song_name.startswith(prefix):
                        song_name = song_name[len(prefix):].strip()
                        break
                song_name = song_name.replace('on spotify', '').strip()
                if not _is_generic_spotify_request(song_name):
                    query = urllib.parse.quote_plus(song_name)
                    url = f'https://open.spotify.com/search/{query}'
                    webbrowser.get().open(url)
                    speak.speak(f"Searching Spotify for {song_name}")
                    return f"Searching Spotify for {song_name}"
            if 'youtube' in data_btn and 'on youtube' in data_btn:
                song_name = data_btn
                for prefix in ['play song', 'play the song', 'play ', 'song ']:
                    if song_name.startswith(prefix):
                        song_name = song_name[len(prefix):].strip()
                        break
                song_name = song_name.replace('on youtube', '').strip()
                if song_name:
                    query = urllib.parse.quote_plus(song_name)
                    url = f'https://www.youtube.com/results?search_query={query}'
                    webbrowser.get().open(url)
                    speak.speak(f"Searching YouTube for {song_name}")
                    return f"Searching YouTube for {song_name}"
            if 'spotify' in data_btn or 'open spotify' in data_btn:
                os.system('start https://open.spotify.com/')
                speak.speak("Spotify is now ready for you, enjoy your music")
                return "Spotify is now ready for you, enjoy your music"
            if 'youtube' in data_btn or 'open youtube' in data_btn:
                os.system('start https://www.youtube.com/')
                speak.speak("YouTube is now ready for you, enjoy your videos")
                return "YouTube is now ready for you, enjoy your videos"
            song_name = data_btn
            for prefix in ['play song', 'play the song', 'play ', 'song ']:
                if song_name.startswith(prefix):
                    song_name = song_name[len(prefix):].strip()
                    break
            if song_name:
                try:
                    songs = os.listdir(MUSIC_FOLDER)
                    target = _find_song(song_name, songs)
                    if target:
                        os.startfile(os.path.join(MUSIC_FOLDER, target))
                        speak.speak(f"Playing {target}")
                        return f"Playing {target}"
                    else:
                        speak.speak("I could not find that song in your music folder")
                        return "I could not find that song in your music folder"
                except Exception:
                    speak.speak("Music folder not found")
                    return "Music folder not found"
            os.system('start https://open.spotify.com/')
            speak.speak("Spotify is now ready for you, enjoy your music")
            return "Spotify is now ready for you, enjoy your music"
        return None


class WebHandler:
    def handle(self, data_btn):
        # Never open browsers for summarize / long paragraph text.
        if _wants_summarize(data_btn) or _is_long_form_text(data_btn):
            return None
        if 'http://' in data_btn or 'https://' in data_btn or 'spotify.com/' in data_btn or 'open.spotify.com' in data_btn:
            url = _extract_url(data_btn)
            if url:
                webbrowser.get().open(url)
                speak.speak("Opening link")
                return "Opening link"
        elif 'iba student portal' in data_btn or 'iba portal' in data_btn:
            url = 'http://sibagrades.iba-suk.edu.pk:86/Default.aspx'
            webbrowser.get().open(url)
            speak.speak("Opening IBA student portal")
            return "Opening IBA student portal"
        elif 'iba elearning' in data_btn or 'elearning iba' in data_btn:
            url = 'https://elearning.iba-suk.edu.pk/my/'
            webbrowser.get().open(url)
            speak.speak("Opening IBA eLearning")
            return "Opening IBA eLearning"
        elif 'search' in data_btn and 'on google' in data_btn and not _is_long_form_text(data_btn):
            topic = data_btn.replace('search', '').replace('on google', '').strip()
            if topic:
                query = urllib.parse.quote_plus(topic)
                url = f'https://www.google.com/search?q={query}'
                webbrowser.get().open(url)
                speak.speak(f"Searching Google for {topic}")
                return f"Searching Google for {topic}"
        elif 'open google' in data_btn or data_btn.strip() == 'google':
            url = 'https://google.com/'
            webbrowser.get().open(url)
            speak.speak("google open")
            return "google open"
        elif ('open youtube' in data_btn or data_btn.strip() == 'youtube') and not _is_long_form_text(data_btn):
            url = 'https://youtube.com/'
            webbrowser.get().open(url)
            speak.speak("YouTube open")
            return "YouTube open"
        return None


class UtilityHandler:
    def handle(self, data_btn):
        if 'weather' in data_btn:
            ans = weather.Weather() if hasattr(weather, "Weather") else "Please use: weather <city>"
            speak.speak(ans)
            return ans
        elif 'convert' in data_btn:
            if ureg is None:
                speak.speak("Unit conversion dependency is missing. Please install pint.")
                return "Unit conversion unavailable: install pint"
            try:
                parts = data_btn.replace('convert', '').strip().split(' to ')
                if len(parts) == 2:
                    from_part = parts[0].strip().split()
                    to_unit = parts[1].strip()
                    if len(from_part) >= 2:
                        value = float(from_part[0])
                        from_unit = ' '.join(from_part[1:])
                        quantity = value * ureg(from_unit)
                        converted = quantity.to(to_unit)
                        result = f"{value} {from_unit} is {converted.magnitude:.2f} {to_unit}"
                        speak.speak(result)
                        return result
            except Exception as e:
                speak.speak("I couldn't perform the conversion. Please try again.")
                return "Conversion failed"
        elif 'system info' in data_btn or 'cpu' in data_btn or 'battery' in data_btn or 'ram' in data_btn:
            if psutil is None:
                speak.speak("System info dependency is missing. Please install psutil.")
                return "System info unavailable: install psutil"
            try:
                if 'cpu' in data_btn:
                    cpu = psutil.cpu_percent(interval=1)
                    result = f"CPU usage is {cpu}%"
                elif 'battery' in data_btn:
                    battery = psutil.sensors_battery()
                    if battery:
                        result = f"Battery is at {battery.percent}%"
                    else:
                        result = "Battery information not available"
                elif 'ram' in data_btn or 'memory' in data_btn:
                    memory = psutil.virtual_memory()
                    result = f"RAM usage is {memory.percent}%"
                else:
                    cpu = psutil.cpu_percent()
                    memory = psutil.virtual_memory()
                    battery = psutil.sensors_battery()
                    battery_info = f", battery {battery.percent}%" if battery else ""
                    result = f"CPU {cpu}%, RAM {memory.percent}%{battery_info}"
                speak.speak(result)
                return result
            except Exception as e:
                speak.speak("Couldn't get system information")
                return "System info unavailable"
        elif 'screenshot' in data_btn or 'capture screen' in data_btn:
            try:
                stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                save_dir = _assistant_screenshot_dir()
                file_path = str((save_dir / f"screenshot_{stamp}.png").resolve())
                if not _capture_screenshot_file(file_path):
                    speak.speak("Screenshot dependency missing. Install pyautogui or pillow.")
                    return "Screenshot dependency missing"
                result = f"Screenshot saved: {file_path}"
                speak.speak(result)
                try:
                    os.startfile(file_path)
                except Exception:
                    pass
                return result
            except Exception as e:
                speak.speak("Couldn't take screenshot")
                return "Screenshot failed"
        return None


class ReminderHandler:
    """Save reminders to Documents/AssistantData/reminders.txt; recall with phrases below."""

    _READ_PHRASES = (
        "my reminders",
        "show reminders",
        "list reminders",
        "what reminders",
        "remind kya",
        "kya remind",
        "mera reminder",
        "reminders dikhao",
        "what did i remind",
        "what did you remind",
        "reminder kya tha",
        "jo remind kiya tha",
    )

    def handle(self, data_btn):
        if any(p in data_btn for p in self._READ_PHRASES):
            path = _assistant_data_dir() / "reminders.txt"
            if not path.is_file():
                msg = "No reminders saved yet. Say something like: remind me to call mom"
                speak.speak(msg)
                return msg
            text = path.read_text(encoding="utf-8", errors="replace").strip()
            if not text:
                msg = "Your reminder list is empty."
                speak.speak(msg)
                return msg
            intro = "Here are your saved reminders."
            speak.speak(intro)
            return intro + "\n" + text

        if "remind me" in data_btn:
            raw = data_btn.split("remind me", 1)[1].strip()
            if raw.startswith("to "):
                raw = raw[3:].strip()
        elif "set reminder" in data_btn:
            raw = data_btn.split("set reminder", 1)[1].strip()
            for prefix in ("for ", "to "):
                if raw.lower().startswith(prefix):
                    raw = raw[len(prefix) :].strip()
                    break
        else:
            return None

        if not raw:
            msg = "What should I remind you about? Say: remind me to call mom"
            speak.speak(msg)
            return msg

        line = f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] {raw}\n"
        rpath = _assistant_data_dir() / "reminders.txt"
        with open(rpath, "a", encoding="utf-8") as f:
            f.write(line)
        speak.speak("Reminder saved.")
        return f"Reminder saved: {raw}. File: {rpath}"


class NoteHandler:
    """Notes in Documents/AssistantData/notes.txt. Save: take note / note ... | Read: show my notes / meri notes ..."""

    _READ_PHRASES = (
        "read my notes",
        "show my notes",
        "show all notes",
        "meri notes",
        "notes batao",
        "notes dikhao",
        "what are my notes",
        "all my notes",
        "notes kya hain",
        "my notes kya hain",
        "read notes",
        "open my notes",
    )

    def handle(self, data_btn):
        if any(p in data_btn for p in self._READ_PHRASES):
            path = _assistant_data_dir() / "notes.txt"
            if not path.is_file():
                msg = "No notes saved yet. Say something like: take note buy milk"
                speak.speak(msg)
                return msg
            text = path.read_text(encoding="utf-8", errors="replace").strip()
            if not text:
                msg = "Your notes file is empty."
                speak.speak(msg)
                return msg
            intro = "Here are your notes."
            speak.speak(intro)
            if len(text) > 3500:
                return (
                    "Your notes (last part; full file at "
                    + str(path)
                    + "):\n"
                    + text[-3500:]
                )
            return "Your notes:\n" + text

        note = None
        if "take note" in data_btn:
            note = data_btn.split("take note", 1)[1].strip()
        elif data_btn.startswith("note "):
            note = data_btn[5:].strip()
        elif data_btn.startswith("note:"):
            note = data_btn.split(":", 1)[1].strip()
        elif data_btn.strip() == "note":
            note = ""

        if note is None:
            return None
        if not note:
            msg = "What should I note? Say: take note and then your text"
            speak.speak(msg)
            return msg

        npath = _assistant_data_dir() / "notes.txt"
        with open(npath, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.datetime.now():%Y-%m-%d %H:%M}] {note}\n")
        speak.speak("Note saved.")
        return f"Note saved. File: {npath}"


class SummarizeHandler:
    """Summarize a paragraph when user says summarize / concise / make it short, etc."""

    def handle(self, data_btn, original_text=None):
        if not _wants_summarize(data_btn):
            return None
        original = (original_text or data_btn or "").strip()
        body = _extract_text_for_summary(original, data_btn)
        if not body:
            msg = (
                "Paste your paragraph with a summarize command. Examples: "
                "'summarize: your long text here' or 'your long text ... summarize it'"
            )
            speak.speak(msg)
            return msg
        summary = summarize_paragraph(body)
        if not summary:
            speak.speak("I could not summarize that text.")
            return "I could not summarize that text."
        result = f"Summary:\n{summary}"
        speak.speak(summary)
        return result


class CalculatorHandler:
    def handle(self, data_btn):
        if 'calculate' in data_btn or 'calc' in data_btn:
            expression = data_btn.replace('calculate', '').replace('calc', '').strip()
            try:
                result = eval(expression)
                speak.speak(f"The result is {result}")
                return f"The result is {result}"
            except:
                speak.speak("I couldn't calculate that")
                return "Calculation failed"
        return None


DB_INSTANCE = DatabaseManager()
SMART_HANDLER = SmartFeatureHandler(DB_INSTANCE)


def Action(send):
    data_btn = send.lower()
    # Summarize always wins — even if other handlers would match "google" / "search" inside text.
    if _wants_summarize(data_btn):
        summary_result = SummarizeHandler().handle(data_btn, send)
        if summary_result:
            return summary_result
    handlers = [
        SummarizeHandler(),
        SMART_HANDLER,
        GreetingHandler(),
        TimeHandler(),
        MusicHandler(),
        WebHandler(),
        UtilityHandler(),
        ReminderHandler(),
        NoteHandler(),
        CalculatorHandler(),
    ]
    for handler in handlers:
        if isinstance(handler, SummarizeHandler):
            result = handler.handle(data_btn, send)
        else:
            result = handler.handle(data_btn)
        if result:
            return result
    speak.speak("I'm not able to understand!")
    return "I'm not able to understand!"