#!/usr/bin/env python3
"""Companion - a little launcher that greets you when the PC boots.

Usage:
    python3 companion.py            # open the popup now
    python3 companion.py --install  # start automatically on every login
    python3 companion.py --remove   # stop starting automatically
"""

import datetime
import os
import subprocess
import sys
import time
import tkinter as tk
import webbrowser
from pathlib import Path

HOME = Path.home()
SCRIPT = Path(__file__).resolve()
AUTOSTART_FILE = HOME / ".config" / "autostart" / "companion.desktop"
MINECRAFT_DIR = HOME / "Downloads" / "minecraft-launcher"
GITHUB_URL = "https://github.com/SAURABH-sys-png/"
BOOT_DELAY_SECONDS = 3

# Colors
BG = "#0d0f1a"
CARD = "#161a2e"
CARD_HOVER = "#222846"
ACCENT = "#00f0ff"
ACCENT2 = "#ff2e88"
TEXT = "#e6e9ff"
MUTED = "#7a80a8"


# ---------- startup (autostart) handling ----------

def is_autostart_enabled():
    return AUTOSTART_FILE.exists()


def enable_autostart():
    AUTOSTART_FILE.parent.mkdir(parents=True, exist_ok=True)
    AUTOSTART_FILE.write_text(
        "[Desktop Entry]\n"
        "Type=Application\n"
        "Name=Companion\n"
        "Comment=Greets you at boot and launches your stuff\n"
        f'Exec={sys.executable} "{SCRIPT}" --boot\n'
        "Terminal=false\n"
        "X-GNOME-Autostart-enabled=true\n"
    )


def disable_autostart():
    AUTOSTART_FILE.unlink(missing_ok=True)


# ---------- actions ----------

def run(*cmd, cwd=None):
    """Start a program fully detached so it keeps running after we exit."""
    try:
        subprocess.Popen(
            list(cmd),
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        return True
    except (FileNotFoundError, PermissionError):
        return False


def open_github():
    webbrowser.open(GITHUB_URL)


def start_streaming():
    run("brave-browser", "--new-window", "https://www.youtube.com", "https://leetcode.com")
    run("obs")
    run("firefox", "--new-window", "https://codeforces.com")


def open_minecraft():
    run("./minecraft-launcher", cwd=MINECRAFT_DIR)


def coding_mode():
    project_dir = HOME / "apps"
    run("code", str(project_dir))
    run("ptyxis", "--new-window", "--working-directory", str(project_dir))


def open_terminal():
    run("ptyxis", "--new-window")


def open_files():
    run("nautilus", str(HOME))


def chill_music():
    webbrowser.open("https://www.youtube.com/results?search_query=lofi+hip+hop+radio")


# (icon, title, subtitle, function)
ACTIONS = [
    ("★", "Open GitHub", "SAURABH-sys-png", open_github),
    ("◉", "Start Streaming", "Brave (YT + LeetCode) · OBS · Firefox (Codeforces)", start_streaming),
    ("▦", "Minecraft", "Launch the Minecraft launcher", open_minecraft),
    ("{ }", "Coding Mode", "VS Code + terminal in ~/apps", coding_mode),
    ("♫", "Chill Music", "Lofi beats on YouTube", chill_music),
    (">_", "Terminal", "Fresh terminal window", open_terminal),
    ("▤", "Files", "Open home folder", open_files),
]


# ---------- UI ----------

def greeting():
    hour = datetime.datetime.now().hour
    if hour < 5:
        return "Still up, dear master?"
    if hour < 12:
        return "Good morning, dear master"
    if hour < 17:
        return "Good afternoon, dear master"
    return "Good evening, dear master"


def uptime_text():
    try:
        seconds = int(float(Path("/proc/uptime").read_text().split()[0]))
    except OSError:
        return ""
    hours, rem = divmod(seconds, 3600)
    return f"up {hours}h {rem // 60}m"


class Companion(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Companion")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.attributes("-topmost", True)
        self.bind("<Escape>", lambda e: self.destroy())

        self._build_header()
        self._build_actions()
        self._build_footer()

        self._center()
        self._fade_in()
        self._tick()

    def _build_header(self):
        header = tk.Frame(self, bg=BG)
        header.pack(fill="x", padx=28, pady=(24, 6))

        tk.Label(header, text=greeting(), bg=BG, fg=ACCENT,
                 font=("Sans", 20, "bold")).pack(anchor="w")
        tk.Label(header, text="What do you want to do today?", bg=BG, fg=TEXT,
                 font=("Sans", 12)).pack(anchor="w", pady=(2, 0))

        self.clock = tk.Label(header, bg=BG, fg=MUTED, font=("Monospace", 10))
        self.clock.pack(anchor="w", pady=(8, 0))

        tk.Frame(self, bg=ACCENT2, height=2).pack(fill="x", padx=28, pady=(10, 14))

    def _build_actions(self):
        grid = tk.Frame(self, bg=BG)
        grid.pack(padx=22)
        for i, (icon, title, subtitle, func) in enumerate(ACTIONS):
            card = self._card(grid, i + 1, icon, title, subtitle, func)
            card.grid(row=i // 2, column=i % 2, padx=6, pady=6, sticky="nsew")
            self.bind(str(i + 1), lambda e, f=func: self._launch(f))

    def _card(self, parent, number, icon, title, subtitle, func):
        card = tk.Frame(parent, bg=CARD, width=300, height=74, cursor="hand2")
        card.pack_propagate(False)

        row = tk.Frame(card, bg=CARD)
        row.pack(fill="both", expand=True, padx=14, pady=10)
        icon_lbl = tk.Label(row, text=icon, bg=CARD, fg=TEXT, font=("Sans", 22))
        icon_lbl.pack(side="left", padx=(0, 12))
        texts = tk.Frame(row, bg=CARD)
        texts.pack(side="left", fill="both", expand=True)
        title_lbl = tk.Label(texts, text=f"{title}", bg=CARD, fg=TEXT,
                             font=("Sans", 12, "bold"), anchor="w")
        title_lbl.pack(fill="x")
        sub_lbl = tk.Label(texts, text=subtitle, bg=CARD, fg=MUTED,
                           font=("Sans", 8), anchor="w", wraplength=210, justify="left")
        sub_lbl.pack(fill="x")
        key_lbl = tk.Label(row, text=str(number), bg=CARD, fg=MUTED, font=("Monospace", 9))
        key_lbl.pack(side="right", anchor="n")

        widgets = [card, row, icon_lbl, texts, title_lbl, sub_lbl, key_lbl]

        def set_hover(on):
            color = CARD_HOVER if on else CARD
            for w in widgets:
                w.configure(bg=color)
            title_lbl.configure(fg=ACCENT if on else TEXT)

        for w in widgets:
            w.bind("<Enter>", lambda e: set_hover(True))
            w.bind("<Leave>", lambda e: set_hover(False))
            w.bind("<Button-1>", lambda e: self._launch(func))
        return card

    def _build_footer(self):
        footer = tk.Frame(self, bg=BG)
        footer.pack(fill="x", padx=28, pady=(14, 20))

        self.autostart_var = tk.BooleanVar(value=is_autostart_enabled())
        tk.Checkbutton(
            footer, text="Show this on startup", variable=self.autostart_var,
            command=self._toggle_autostart, bg=BG, fg=TEXT, selectcolor=CARD,
            activebackground=BG, activeforeground=ACCENT, highlightthickness=0,
            font=("Sans", 10), cursor="hand2",
        ).pack(side="left")

        close = tk.Label(footer, text="Not now  ✕", bg=BG, fg=MUTED,
                         font=("Sans", 10), cursor="hand2")
        close.pack(side="right")
        close.bind("<Button-1>", lambda e: self.destroy())
        close.bind("<Enter>", lambda e: close.configure(fg=ACCENT2))
        close.bind("<Leave>", lambda e: close.configure(fg=MUTED))

        self.status = tk.Label(self, text="Press 1-7 or click · Esc to close",
                               bg=BG, fg=MUTED, font=("Sans", 8))
        self.status.pack(pady=(0, 12))

    def _toggle_autostart(self):
        if self.autostart_var.get():
            enable_autostart()
            self.status.configure(text="Companion will greet you on next boot", fg=ACCENT)
        else:
            disable_autostart()
            self.status.configure(text="Startup disabled — run companion.py to open me again",
                                  fg=ACCENT2)

    def _launch(self, func):
        func()
        self.status.configure(text="On it, master!", fg=ACCENT)
        self.after(700, self.destroy)

    def _tick(self):
        now = datetime.datetime.now().strftime("%A, %d %b  ·  %H:%M:%S")
        self.clock.configure(text=f"{now}   {uptime_text()}")
        self.after(1000, self._tick)

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 3
        self.geometry(f"+{x}+{y}")

    def _fade_in(self, alpha=0.0):
        try:
            self.attributes("-alpha", alpha)
        except tk.TclError:
            return
        if alpha < 0.97:
            self.after(15, self._fade_in, alpha + 0.06)


def main():
    args = sys.argv[1:]
    if "--install" in args:
        enable_autostart()
        print(f"Installed: {AUTOSTART_FILE}")
        return
    if "--remove" in args:
        disable_autostart()
        print("Removed from startup.")
        return
    if "--boot" in args:
        time.sleep(BOOT_DELAY_SECONDS)
    Companion().mainloop()


if __name__ == "__main__":
    main()
