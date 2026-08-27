import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import sys
import threading

# Support both normal run and PyInstaller bundle
if getattr(sys, "frozen", False):
    _base = Path(sys._MEIPASS)
else:
    _base = Path(__file__).parent

sys.path.insert(0, str(_base))
from kuomat_pelaa_poster import make_poster

DARK_BG = "#070f14"
CARD_BG = "#0c2428"
ACCENT = "#5ceeee"
TEXT_FG = "#f2f7f8"
BTN_BG = "#0c3a40"
SLOT_W = 200
SLOT_H = 140


class ImageSlot(tk.Frame):
    def __init__(self, master, label, **kw):
        super().__init__(master, bg=CARD_BG, width=SLOT_W, height=SLOT_H,
                         highlightbackground=ACCENT, highlightthickness=1, **kw)
        self.pack_propagate(False)
        self.path = None

        self._label_text = label
        self._inner = tk.Frame(self, bg=CARD_BG)
        self._inner.place(relx=0.5, rely=0.5, anchor="center")

        self._icon = tk.Label(self._inner, text="＋", font=("Arial", 28),
                              fg=ACCENT, bg=CARD_BG)
        self._icon.pack()
        self._text = tk.Label(self._inner, text=label, font=("Arial", 11),
                              fg="#8ab8be", bg=CARD_BG)
        self._text.pack()

        self.bind("<Button-1>", self._pick)
        self._icon.bind("<Button-1>", self._pick)
        self._text.bind("<Button-1>", self._pick)
        self._configure_hover()

    def _configure_hover(self):
        for w in (self, self._icon, self._text, self._inner):
            w.bind("<Enter>", lambda e: self.configure(highlightbackground="#a0fafa"))
            w.bind("<Leave>", lambda e: self.configure(highlightbackground=ACCENT))

    def _pick(self, _event=None):
        p = filedialog.askopenfilename(
            title=f"Valitse {self._label_text}",
            filetypes=[("Kuvat", "*.jpg *.jpeg *.png *.webp"), ("Kaikki", "*.*")]
        )
        if p:
            self.path = p
            name = Path(p).name
            self._icon.configure(text="✓", fg="#50e8a0")
            self._text.configure(text=name[:26] + ("…" if len(name) > 26 else ""),
                                  fg=TEXT_FG)

    def get(self):
        return self.path

    def set_default_label(self, label):
        self._label_text = label
        if self.path is None:
            self._text.configure(text=label)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Kuomat Pelaa – Posterigeneraattori")
        self.configure(bg=DARK_BG)
        self.resizable(False, False)
        self._build()

    def _build(self):
        pad = dict(padx=24, pady=12)

        # Title
        tk.Label(self, text="KUOMAT PELAA", font=("Arial", 18, "bold"),
                 fg=ACCENT, bg=DARK_BG).pack(pady=(24, 2))
        tk.Label(self, text="Posterigeneraattori", font=("Arial", 11),
                 fg="#8ab8be", bg=DARK_BG).pack(pady=(0, 8))

        # Yksi / kaksi peliä -valinta
        self.single_mode = tk.BooleanVar(value=False)
        mode_frame = tk.Frame(self, bg=DARK_BG)
        mode_frame.pack(pady=(0, 10))

        radio_style = dict(
            variable=self.single_mode, command=self._toggle_mode,
            font=("Arial", 11), fg="#8ab8be", bg=DARK_BG,
            activebackground=DARK_BG, activeforeground=ACCENT,
            selectcolor=CARD_BG, cursor="hand2",
            highlightthickness=0, bd=0
        )
        tk.Radiobutton(mode_frame, text="Kaksi peliä (kaksi kuvaa)",
                       value=False, **radio_style).pack(side="left", padx=(0, 12))
        tk.Radiobutton(mode_frame, text="Yksi peli (yksi kuva)",
                       value=True, **radio_style).pack(side="left")

        # Image slots
        slots_frame = tk.Frame(self, bg=DARK_BG)
        slots_frame.pack(**pad)

        self.slot_top = ImageSlot(slots_frame, "Yläkuva")
        self.slot_top.grid(row=0, column=0, padx=(0, 12))

        self.slot_bottom = ImageSlot(slots_frame, "Alakuva")
        self.slot_bottom.grid(row=0, column=1, padx=(12, 0))

        # Body text
        tk.Label(self, text="Jakson kuvaus", font=("Arial", 11),
                 fg=TEXT_FG, bg=DARK_BG, anchor="w").pack(fill="x", padx=24)

        text_frame = tk.Frame(self, bg=ACCENT, padx=1, pady=1)
        text_frame.pack(padx=24, pady=(4, 16), fill="x")

        self.body_text = tk.Text(text_frame, height=5, font=("Arial", 12),
                                  bg=CARD_BG, fg=TEXT_FG, insertbackground=ACCENT,
                                  relief="flat", padx=10, pady=8,
                                  wrap="word")
        self.body_text.pack(fill="x")

        # Generate button
        self.btn = tk.Button(self, text="✦  Luo posteri",
                              font=("Arial", 13, "bold"),
                              bg=BTN_BG, fg=ACCENT, activebackground="#0f4a52",
                              activeforeground="#a0fafa", relief="flat",
                              cursor="hand2", pady=12,
                              command=self._generate)
        self.btn.pack(fill="x", padx=24, pady=(0, 8))

        # Status bar
        self.status = tk.Label(self, text="", font=("Arial", 10),
                                fg="#8ab8be", bg=DARK_BG)
        self.status.pack(pady=(0, 20))

    def _toggle_mode(self):
        if self.single_mode.get():
            self.slot_bottom.grid_remove()
            self.slot_top.set_default_label("Kuva")
        else:
            self.slot_bottom.grid()
            self.slot_top.set_default_label("Yläkuva")

    def _generate(self):
        single = self.single_mode.get()
        top = self.slot_top.get()
        bottom = None if single else self.slot_bottom.get()
        body = self.body_text.get("1.0", "end").strip()

        if not top:
            messagebox.showwarning("Puuttuu", "Valitse kuva." if single else "Valitse yläkuva.")
            return
        if not single and not bottom:
            messagebox.showwarning("Puuttuu", "Valitse alakuva.")
            return
        if not body:
            messagebox.showwarning("Puuttuu", "Kirjoita jakson kuvaus.")
            return

        self.btn.configure(state="disabled", text="⏳  Luodaan…")
        self.status.configure(text="")
        threading.Thread(target=self._run, args=(top, bottom, body), daemon=True).start()

    def _run(self, top, bottom, body):
        try:
            if getattr(sys, "frozen", False):
                out = Path(sys.executable).parent / "jakso.png"
            else:
                out = Path(__file__).parent / "jakso.png"
            make_poster(top, bottom, body, str(out))
            self.after(0, self._done, str(out))
        except Exception as e:
            self.after(0, self._error, str(e))

    def _done(self, path):
        self.btn.configure(state="normal", text="✦  Luo posteri")
        self.status.configure(text=f"Valmis: {path}", fg="#50e8a0")

    def _error(self, msg):
        self.btn.configure(state="normal", text="✦  Luo posteri")
        self.status.configure(text="Virhe posterin luonnissa", fg="#e86060")
        messagebox.showerror("Virhe", msg)


if __name__ == "__main__":
    App().mainloop()
