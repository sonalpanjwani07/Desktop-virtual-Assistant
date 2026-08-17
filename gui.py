from tkinter import *
from tkinter import ttk
import threading
import math
import time

import action
import speak
import spech_to_text

try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

from assistant.gui.animation_controller import GUIAnimationController


def remove_white_background(image, threshold=235):
    image = image.convert("RGBA")
    pixels = list(image.getdata())
    cleaned = []
    for r, g, b, a in pixels:
        if r >= threshold and g >= threshold and b >= threshold:
            cleaned.append((r, g, b, 0))
        else:
            cleaned.append((r, g, b, a))
    image.putdata(cleaned)
    return image


class ModernAssistantGUI:
    def __init__(self):
        self.root = Tk()
        self.root.title("AI Assistant Pro")
        self.root.geometry("620x760")
        self.root.minsize(620, 760)
        self.root.config(bg="#E6D6F2")
        # Lilac palette used across UI for a soft aesthetic.
        self.palette = {
            "bg_top": "#E6D6F2",
            "bg_mid": "#C8A2C8",
            "bg_bottom": "#A67BA0",
            "button": "#BFA2DB",
            "button_hover": "#D8C1EE",
            "text_dark": "#3D2C4A",
            "chat_surface": "#F4EAFB",
            "user_bubble": "#C7A9E6",
            "bot_bubble": "#EADAF8",
            "white": "#FFFFFF",
        }
        self.gradient_phase = 0.0
        self._gradient_running = False
        self.status_var = StringVar(value="Idle")
        self._status_last = "Idle"

        # Command history (typed + spoken).
        self._history = []
        self._history_pos = 0

        # Listening mic pulse animation state.
        self._mic_pulse_after = None
        self._mic_pulse_phase = 0.0

        # Theme toggle (keeps layout identical; switches palette only).
        self._theme_name = "lilac"
        self._palettes = {
            "lilac": {
                "bg_top": "#E6D6F2",
                "bg_mid": "#C8A2C8",
                "bg_bottom": "#A67BA0",
                "button": "#BFA2DB",
                "button_hover": "#D8C1EE",
                "text_dark": "#3D2C4A",
                "chat_surface": "#F4EAFB",
                "user_bubble": "#C7A9E6",
                "bot_bubble": "#EADAF8",
                "white": "#FFFFFF",
            },
            "midnight": {
                "bg_top": "#1C1526",
                "bg_mid": "#2A1F3B",
                "bg_bottom": "#3A2A52",
                "button": "#6F57A8",
                "button_hover": "#8A73C6",
                "text_dark": "#F3EFFF",
                "chat_surface": "#221A2F",
                "user_bubble": "#4E3B77",
                "bot_bubble": "#2F2444",
                "white": "#2B203D",
            },
        }

        speak.set_status_callback(self._set_status)
        spech_to_text.set_status_callback(self._set_status)

        self.bg_canvas = Canvas(self.root, highlightthickness=0, bd=0)
        self.bg_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._build_header()
        self._build_chat_area()
        self._build_input_area()
        self._load_avatar()
        self._fade_in()

        self.root.bind("<Configure>", self._on_resize)
        self.entry.bind("<Return>", lambda _e: self.user_send())
        self.entry.bind("<Up>", self._history_up)
        self.entry.bind("<Down>", self._history_down)
        self.root.bind("<Control-t>", lambda _e: self.toggle_theme())

    def _set_status(self, value: str):
        # Thread-safe UI update: speech callbacks may come from worker threads.
        def _apply():
            self._status_last = value
            self.status_var.set(value)
            if value.startswith("Listening"):
                self._start_mic_pulse()
            else:
                self._stop_mic_pulse()

        try:
            if threading.current_thread() is threading.main_thread():
                _apply()
            else:
                self.root.after(0, _apply)
        except Exception:
            # If UI is closing, ignore status updates.
            pass

    def _build_header(self):
        self.title_label = Label(
            self.root,
            text="AI-Virtual Assistant",
            font=("Segoe UI", 20, "italic"),
            fg=self.palette["text_dark"],
            bg=self.palette["bg_top"],
        )
        self.title_label.place(relx=0.5, rely=0.05, anchor="center")

        self.status_label = Label(
            self.root,
            textvariable=self.status_var,
            font=("Segoe UI", 11, "italic"),
            fg=self.palette["text_dark"],
            bg=self.palette["bg_top"],
        )
        self.status_label.place(relx=0.5, rely=0.095, anchor="center")

    def _build_chat_area(self):
        self.chat_outer = Frame(self.root, bg=self.palette["bg_mid"])
        self.chat_outer.place(relx=0.08, rely=0.28, relwidth=0.84, relheight=0.5)

        # Soft "glass" surface illusion: slightly brighter inner surface.
        self.chat_canvas = Canvas(self.chat_outer, bg=self.palette["chat_surface"], highlightthickness=0)
        self.chat_scroll = ttk.Scrollbar(self.chat_outer, orient="vertical", command=self.chat_canvas.yview)
        self.chat_frame = Frame(self.chat_canvas, bg=self.palette["chat_surface"])

        self.chat_frame.bind(
            "<Configure>", lambda _e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )
        self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=self.chat_scroll.set)

        self.chat_canvas.pack(side=LEFT, fill=BOTH, expand=True)
        self.chat_scroll.pack(side=RIGHT, fill=Y)

    def _build_input_area(self):
        self.input_frame = Frame(self.root, bg=self.palette["bg_mid"])
        self.input_frame.place(relx=0.08, rely=0.82, relwidth=0.84, relheight=0.13)

        self.entry = Entry(
            self.input_frame,
            font=("Segoe UI", 12, "italic"),
            justify=CENTER,
            fg=self.palette["text_dark"],
            bg=self.palette["white"],
            insertbackground=self.palette["text_dark"],
            relief=FLAT,
        )
        self.entry.place(relx=0.02, rely=0.08, relwidth=0.96, relheight=0.35)

        self.btn_mic = self._make_round_button(self.input_frame, "🎤", self.ask, 0.20)
        self.btn_send = self._make_round_button(self.input_frame, "➤", self.user_send, 0.50)
        self.btn_clear = self._make_round_button(self.input_frame, "🗑", self.clear_chat, 0.80)

    def _make_round_button(self, parent, text, command, relx):
        btn_canvas = Canvas(parent, width=70, height=38, bg=self.palette["bg_mid"], highlightthickness=0)
        btn_canvas.place(relx=relx, rely=0.72, anchor="center")
        # Soft glow layer for hover effect.
        glow = btn_canvas.create_oval(2, 1, 68, 37, fill="#F8F1FF", outline="")
        btn_canvas.itemconfigure(glow, state="hidden")
        oval = btn_canvas.create_oval(5, 4, 65, 34, fill=self.palette["button"], outline=self.palette["button"])
        txt = btn_canvas.create_text(35, 19, text=text, fill=self.palette["white"], font=("Segoe UI Emoji", 14, "bold"))

        def click(_event=None):
            # Smooth click feedback: scale down then return.
            btn_canvas.scale("all", 35, 19, 0.85, 0.85)
            self.root.after(90, lambda: btn_canvas.scale("all", 35, 19, 1 / 0.85, 1 / 0.85))
            command()

        def on_enter(_event=None):
            btn_canvas.itemconfigure(glow, state="normal")
            btn_canvas.itemconfigure(oval, fill=self.palette["button_hover"], outline=self.palette["button_hover"])
            btn_canvas.itemconfigure(txt, fill=self.palette["text_dark"])

        def on_leave(_event=None):
            btn_canvas.itemconfigure(glow, state="hidden")
            btn_canvas.itemconfigure(oval, fill=self.palette["button"], outline=self.palette["button"])
            btn_canvas.itemconfigure(txt, fill=self.palette["white"])

        btn_canvas.bind("<Button-1>", click)
        btn_canvas.bind("<Enter>", on_enter)
        btn_canvas.bind("<Leave>", on_leave)
        return btn_canvas

    def _history_up(self, _event=None):
        if not self._history:
            return "break"
        self._history_pos = max(0, self._history_pos - 1)
        self.entry.delete(0, END)
        self.entry.insert(0, self._history[self._history_pos])
        return "break"

    def _history_down(self, _event=None):
        if not self._history:
            return "break"
        self._history_pos = min(len(self._history), self._history_pos + 1)
        self.entry.delete(0, END)
        if self._history_pos < len(self._history):
            self.entry.insert(0, self._history[self._history_pos])
        return "break"

    def _remember_history(self, text: str):
        t = (text or "").strip()
        if not t:
            return
        if self._history and self._history[-1] == t:
            return
        self._history.append(t)
        self._history = self._history[-50:]
        self._history_pos = len(self._history)

    def _load_avatar(self):
        self.avatar_photo = None
        self.avatar_item = None
        self._avatar_sizes = []
        self._avatar_size_index = 0
        self._avatar_base_image = None
        avatar_img = None
        if Image and ImageTk:
            for candidate in (
                "assistant/assets/avatar.png",
                "image/image/assistant.png",
                "image/assistant.png",
                "assistant.png",
                "assistant.jpeg",
            ):
                try:
                    img = Image.open(candidate).convert("RGBA")
                    # Keep transparent look for avatar.
                    img = remove_white_background(img)
                    self._avatar_base_image = img
                    self._avatar_sizes = [
                        ImageTk.PhotoImage(img.resize((size, size), Image.LANCZOS))
                        for size in range(116, 125)
                    ]
                    avatar_img = self._avatar_sizes[4]
                    break
                except Exception:
                    avatar_img = None
        self.avatar_photo = avatar_img
        if self.avatar_photo:
            self.avatar_item = self.bg_canvas.create_image(310, 155, image=self.avatar_photo)
            self.anim = GUIAnimationController(
                self.root,
                self.bg_canvas,
                self.avatar_item,
                0.5,
                0.20,
                breathing_callback=self._set_avatar_breathing,
            )
            self.anim.animate_avatar()

    def _set_avatar_breathing(self, scale):
        # Slight breathing zoom by switching between pre-built avatar sizes.
        if not self._avatar_sizes:
            return
        idx = int((scale - 0.97) / 0.06 * (len(self._avatar_sizes) - 1))
        idx = max(0, min(len(self._avatar_sizes) - 1, idx))
        if idx != self._avatar_size_index:
            self._avatar_size_index = idx
            self.avatar_photo = self._avatar_sizes[idx]
            self.bg_canvas.itemconfigure(self.avatar_item, image=self.avatar_photo)

    def _blend(self, c1, c2, t):
        c1 = c1.lstrip("#")
        c2 = c2.lstrip("#")
        r1, g1, b1 = int(c1[:2], 16), int(c1[2:4], 16), int(c1[4:], 16)
        r2, g2, b2 = int(c2[:2], 16), int(c2[2:4], 16), int(c2[4:], 16)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def _draw_gradient(self):
        if self._gradient_running:
            return
        self._gradient_running = True

        self._draw_gradient_frame()

    def _draw_gradient_frame(self):
        self.bg_canvas.delete("bg")
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        # Slow animated lilac shift.
        self.gradient_phase += 0.02
        wave = (math.sin(self.gradient_phase) + 1) / 2
        top = self._blend(self.palette["bg_top"], self.palette["bg_mid"], wave * 0.25)
        mid = self._blend(self.palette["bg_mid"], self.palette["bg_bottom"], wave * 0.25)
        bottom = self._blend(self.palette["bg_bottom"], self.palette["bg_mid"], wave * 0.2)
        for y in range(0, h + 1, 4):
            ratio = y / max(h, 1)
            blend_source = top if ratio < 0.5 else mid
            blend_target = mid if ratio < 0.5 else bottom
            local_t = ratio * 2 if ratio < 0.5 else (ratio - 0.5) * 2
            color = self._blend(blend_source, blend_target, local_t)
            self.bg_canvas.create_rectangle(0, y, w, y + 4, fill=color, outline="", tags="bg")
        self.bg_canvas.tag_lower("bg")
        self.root.after(120, self._draw_gradient_frame)

    def _on_resize(self, event=None):
        if event and event.widget != self.root:
            return
        self._draw_gradient()

    def _fade_in(self):
        self.root.attributes("-alpha", 0.0)

        def step(val=0.0):
            val += 0.08
            self.root.attributes("-alpha", min(val, 1.0))
            if val < 1.0:
                self.root.after(25, lambda: step(val))

        step(0.0)

    def add_message_bubble(self, message: str, sender: str):
        row = len(self.chat_frame.winfo_children())
        anchor = "e" if sender == "user" else "w"
        bg = self.palette["user_bubble"] if sender == "user" else self.palette["bot_bubble"]
        fg = self.palette["text_dark"]

        container = Frame(self.chat_frame, bg=self.palette["chat_surface"])
        # Animate "slide in" by easing padding from larger to normal.
        container.grid(row=row, column=0, sticky="ew", padx=8, pady=12)
        container.grid_columnconfigure(0, weight=1)

        bubble = Label(
            container,
            text=message,
            bg=bg,
            fg=fg,
            font=("Segoe UI", 11, "italic"),
            wraplength=360,
            justify=LEFT,
            padx=14,
            pady=10,
            bd=0,
        )
        bubble.pack(anchor=anchor)

        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

        def _ease_pady(step=0):
            # 6 steps from 12 -> 5
            target = 5
            start = 12
            t = step / 6
            eased = int(start + (target - start) * (1 - (1 - t) * (1 - t)))
            try:
                container.grid_configure(pady=max(target, eased))
            except Exception:
                return
            if step < 6:
                self.root.after(22, lambda: _ease_pady(step + 1))

        _ease_pady(0)

    def _bot_typing_effect(self, full_text: str):
        row = len(self.chat_frame.winfo_children())
        container = Frame(self.chat_frame, bg=self.palette["chat_surface"])
        container.grid(row=row, column=0, sticky="ew", padx=8, pady=5)
        label = Label(
            container,
            text="",
            bg=self.palette["bot_bubble"],
            fg=self.palette["text_dark"],
            font=("Segoe UI", 11, "italic"),
            wraplength=360,
            justify=LEFT,
            padx=14,
            pady=10,
            bd=0,
        )
        label.pack(anchor="w")
        self.anim.type_text(label, full_text, step_ms=22) if hasattr(self, "anim") else label.config(text=full_text)
        self.chat_canvas.update_idletasks()
        self.chat_canvas.yview_moveto(1.0)

    def user_send(self):
        user_text = self.entry.get().strip()
        if not user_text:
            return
        self.entry.delete(0, END)
        self._remember_history(user_text)
        self.add_message_bubble(user_text, sender="user")
        self._set_status("Thinking...")
        self._process_reply_async(user_text)

    def _process_reply_async(self, text: str):
        def _run():
            try:
                bot = action.Action(text)
            except Exception:
                bot = None

            def _apply():
                try:
                    if bot and str(bot).lower() in ("ok sir", "shutdown"):
                        self._bot_typing_effect(str(bot))
                        self.root.after(500, self.root.destroy)
                        return
                    self._bot_typing_effect(str(bot) if bot else "I am here.")
                finally:
                    # Let speech callbacks drive Speaking/Idle; otherwise, stay safe.
                    if not self._status_last.startswith("Speaking"):
                        self._set_status("Idle")

            try:
                self.root.after(0, _apply)
            except Exception:
                pass

        threading.Thread(target=_run, daemon=True).start()

    def ask(self):
        def _run():
            self._set_status("Listening...")
            query = spech_to_text.spech_to_text()
            if not query:
                self._set_status("Idle")
                return
            self._remember_history(query)
            self.root.after(0, lambda: self.add_message_bubble(query, "user"))
            self.root.after(0, lambda: self._process_reply_async(query))

        threading.Thread(target=_run, daemon=True).start()

    def clear_chat(self):
        for child in self.chat_frame.winfo_children():
            child.destroy()

    def run(self):
        self._draw_gradient()
        self.add_message_bubble("Hi. I am your modern AI assistant. How can I help you?", sender="bot")
        self.root.mainloop()

    def _start_mic_pulse(self):
        if self._mic_pulse_after is not None:
            return

        def _tick():
            if not self._status_last.startswith("Listening"):
                self._stop_mic_pulse()
                return
            self._mic_pulse_phase += 0.22
            pulse = 1.0 + 0.05 * (math.sin(self._mic_pulse_phase) + 1) / 2
            try:
                # Pulse the mic button canvas content around its center.
                c = self.btn_mic
                c.scale("all", 35, 19, pulse, pulse)
                self.root.after(40, lambda: c.scale("all", 35, 19, 1 / pulse, 1 / pulse))
            except Exception:
                self._stop_mic_pulse()
                return
            self._mic_pulse_after = self.root.after(120, _tick)

        self._mic_pulse_after = self.root.after(60, _tick)

    def _stop_mic_pulse(self):
        if self._mic_pulse_after is None:
            return
        try:
            self.root.after_cancel(self._mic_pulse_after)
        except Exception:
            pass
        self._mic_pulse_after = None

    def toggle_theme(self):
        # Optional enhancement: Ctrl+T to toggle palette.
        self._theme_name = "midnight" if self._theme_name == "lilac" else "lilac"
        self.palette = self._palettes[self._theme_name]
        try:
            self.root.config(bg=self.palette["bg_top"])
            self.title_label.config(bg=self.palette["bg_top"], fg=self.palette["text_dark"])
            self.status_label.config(bg=self.palette["bg_top"], fg=self.palette["text_dark"])
            self.chat_outer.config(bg=self.palette["bg_mid"])
            self.chat_canvas.config(bg=self.palette["chat_surface"])
            self.chat_frame.config(bg=self.palette["chat_surface"])
            self.input_frame.config(bg=self.palette["bg_mid"])
            self.entry.config(
                fg=self.palette["text_dark"],
                bg=self.palette["white"],
                insertbackground=self.palette["text_dark"],
            )
            # Recolor button canvases.
            for btn in (self.btn_mic, self.btn_send, self.btn_clear):
                btn.config(bg=self.palette["bg_mid"])
                # item ids are stable by creation order; update fills best-effort.
                try:
                    items = btn.find_all()
                    if len(items) >= 3:
                        glow, oval, txt = items[0], items[1], items[2]
                        btn.itemconfigure(oval, fill=self.palette["button"], outline=self.palette["button"])
                        btn.itemconfigure(txt, fill=self.palette["white"])
                        btn.itemconfigure(glow, fill="#F8F1FF" if self._theme_name == "lilac" else "#2F2444")
                except Exception:
                    pass
            self._draw_gradient()
        except Exception:
            pass


if __name__ == "__main__":
    ModernAssistantGUI().run()