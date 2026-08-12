"""
ui/app_window.py
------------------
Poora GUI is file mein hai. customtkinter use kiya hai (modern, dark-theme
tkinter wrapper). Ye file sirf "display + button clicks" handle karti hai --
actual hardware/analysis logic core/ folder ki files mein hai.

Layout (responsive, grid-based):

    ┌─────────────────────────────────────────────────────────┐
    │  HEADER  (title, version, live status dot)               │
    ├─────────────────────────────────────────────────────────┤
    │  CONNECTION CARD  (port, baud, model, action buttons)     │
    ├───────────────────────────┬───────────────────────────────┤
    │  LIVE LOG CONSOLE (60%)    │  LOCAL ANALYSIS RESULTS (40%)  │
    │  (grows/shrinks with       │  (grows/shrinks with            │
    │   window resize)           │   window resize)                 │
    └───────────────────────────┴───────────────────────────────┘
    │  FOOTER STATUS BAR                                          │
    └─────────────────────────────────────────────────────────┘

Grid weights isliye set kiye hain taaki window resize karne par log/results
panels sahi tarah se stretch/shrink hon (responsive), sirf fixed-size na rahein.
"""

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import pyperclip

import config
from core.uart_reader import UartReader, list_available_ports, save_log_to_file
from core.analyzer import run_local_analysis, format_local_analysis_summary, build_ai_prompt


# ---------------------------------------------------------------------------
# Color palette -- ek jagah define kiya hai taaki consistent theme rahe
# ---------------------------------------------------------------------------
COLORS = {
    "bg":            "#0f1117",
    "card":          "#171a23",
    "card_border":   "#262b38",
    "accent":        "#5b8cff",
    "accent_hover":  "#4a75e0",
    "success":       "#2fbf71",
    "success_hover": "#25a05e",
    "danger":        "#e5484d",
    "danger_hover":  "#c93e42",
    "warning":       "#f5a623",
    "text_dim":      "#8b93a7",
    "text_bright":   "#eef1f8",
    "console_bg":    "#0b0d12",
}


class AppWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode(config.UI_APPEARANCE_MODE)
        ctk.set_default_color_theme(config.UI_COLOR_THEME)

        self.title(f"{config.APP_NAME} v{config.APP_VERSION}")
        self.geometry(config.UI_WINDOW_SIZE)
        self.minsize(880, 560)                     # bahut chhota resize na ho sake
        self.configure(fg_color=COLORS["bg"])

        self.reader = None            # UartReader instance, jab connect hoga tab banega
        self.current_log_text = ""    # Abhi tak capture hua poora log
        self.last_ai_prompt = ""      # Last generated AI prompt (copy button ke liye)

        self._build_layout()
        self._refresh_ports()

    # ------------------------------------------------------------------
    # Layout construction
    # ------------------------------------------------------------------
    def _build_layout(self):
        # Root grid: row 0 = header, row 1 = connection card, row 2 = main
        # content (expands), row 3 = footer status bar.
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)   # sirf content area vertically grow kare

        self._build_header()
        self._build_connection_card()
        self._build_main_content()
        self._build_footer()

    # ---- Header -------------------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=0,
                               border_width=0, height=64)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        # Small accent dot as a lightweight "logo"
        logo_dot = ctk.CTkFrame(header, fg_color=COLORS["accent"], corner_radius=8,
                                 width=36, height=36)
        logo_dot.grid(row=0, column=0, padx=(20, 12), pady=14)
        logo_dot.grid_propagate(False)
        ctk.CTkLabel(logo_dot, text="⚡", font=("Segoe UI", 16), text_color="white").place(
            relx=0.5, rely=0.5, anchor="center")

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="w", pady=10)
        ctk.CTkLabel(title_frame, text=config.APP_NAME,
                     font=("Segoe UI Semibold", 18), text_color=COLORS["text_bright"]
                     ).pack(anchor="w")
        ctk.CTkLabel(title_frame, text=f"v{config.APP_VERSION}  ·  UART Boot-Log Diagnostics",
                     font=("Segoe UI", 11), text_color=COLORS["text_dim"]
                     ).pack(anchor="w")

        # Owner / developer credit -- top-right corner of the dashboard
        owner_label = ctk.CTkLabel(header, text="Riaz Ahmed",
                                    font=("Segoe UI", 11), text_color=COLORS["text_dim"])
        owner_label.grid(row=0, column=2, padx=(0, 20), sticky="e")

        # Live status indicator (dot + text) on the right
        status_wrap = ctk.CTkFrame(header, fg_color="transparent")
        status_wrap.grid(row=0, column=3, padx=(0, 20), sticky="e")

        self.status_dot = ctk.CTkLabel(status_wrap, text="●", font=("Segoe UI", 14),
                                        text_color=COLORS["text_dim"])
        self.status_dot.pack(side="left", padx=(0, 6))
        self.status_label = ctk.CTkLabel(status_wrap, text="Idle",
                                          font=("Segoe UI", 12), text_color=COLORS["text_dim"])
        self.status_label.pack(side="left")

    # ---- Connection / controls card -----------------------------------
    def _build_connection_card(self):
        card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=12,
                             border_width=1, border_color=COLORS["card_border"])
        card.grid(row=1, column=0, sticky="ew", padx=16, pady=(16, 10))

        # Responsive: columns 1,3,5 (the input widgets) can stretch a bit
        for col in (1, 3, 5):
            card.grid_columnconfigure(col, weight=1)

        pad = {"padx": (4, 14), "pady": 14}

        ctk.CTkLabel(card, text="Port", font=("Segoe UI", 11),
                     text_color=COLORS["text_dim"]).grid(row=0, column=0, sticky="w", padx=(16, 4))
        self.port_dropdown = ctk.CTkComboBox(card, values=[], width=170,
                                              border_color=COLORS["card_border"])
        self.port_dropdown.grid(row=0, column=1, sticky="ew", **pad)

        refresh_btn = ctk.CTkButton(card, text="⟳", width=36, fg_color=COLORS["card_border"],
                                     hover_color=COLORS["accent"], command=self._refresh_ports)
        refresh_btn.grid(row=0, column=2, padx=(0, 14), pady=14)

        ctk.CTkLabel(card, text="Baud Rate", font=("Segoe UI", 11),
                     text_color=COLORS["text_dim"]).grid(row=0, column=3, sticky="w", padx=(0, 4))
        baud_values = [f"{rate} ({label})" for rate, label in config.BAUD_RATE_OPTIONS]
        self.baud_dropdown = ctk.CTkComboBox(card, values=baud_values, width=220,
                                              border_color=COLORS["card_border"])
        self.baud_dropdown.set(baud_values[0])
        self.baud_dropdown.grid(row=0, column=4, sticky="ew", **pad)

        ctk.CTkLabel(card, text="Phone Model", font=("Segoe UI", 11),
                     text_color=COLORS["text_dim"]).grid(row=0, column=5, sticky="w", padx=(0, 4))
        self.model_entry = ctk.CTkEntry(card, width=160, placeholder_text="e.g. Redmi Note 10",
                                         border_color=COLORS["card_border"])
        self.model_entry.grid(row=0, column=6, sticky="ew", padx=(4, 16), pady=14)

        # ---- Action buttons row ----
        action_row = ctk.CTkFrame(card, fg_color="transparent")
        action_row.grid(row=1, column=0, columnspan=7, sticky="ew", padx=16, pady=(0, 16))

        self.start_btn = ctk.CTkButton(
            action_row, text="▶  Start Capture", height=36, corner_radius=8,
            fg_color=COLORS["success"], hover_color=COLORS["success_hover"],
            font=("Segoe UI Semibold", 12), command=self._on_start_clicked)
        self.start_btn.pack(side="left", padx=(0, 8))

        self.stop_btn = ctk.CTkButton(
            action_row, text="■  Stop", height=36, corner_radius=8,
            fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
            font=("Segoe UI Semibold", 12), command=self._on_stop_clicked, state="disabled")
        self.stop_btn.pack(side="left", padx=8)

        self.analyze_btn = ctk.CTkButton(
            action_row, text="🔍  Run Local Analysis", height=36, corner_radius=8,
            fg_color=COLORS["card_border"], hover_color=COLORS["accent"],
            font=("Segoe UI", 12), command=self._on_analyze_clicked)
        self.analyze_btn.pack(side="left", padx=8)

        self.copy_ai_btn = ctk.CTkButton(
            action_row, text="📋  Copy AI Prompt", height=36, corner_radius=8,
            fg_color=COLORS["card_border"], hover_color=COLORS["accent"],
            font=("Segoe UI", 12), command=self._on_copy_ai_clicked)
        self.copy_ai_btn.pack(side="left", padx=8)

    # ---- Main content: log console (left) + results (right) ----------
    def _build_main_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 10))

        # 60/40 split, dono panels resize hote hain jab window resize ho
        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        # ---- Live log console (card) ----
        log_card = ctk.CTkFrame(content, fg_color=COLORS["card"], corner_radius=12,
                                 border_width=1, border_color=COLORS["card_border"])
        log_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        log_card.grid_columnconfigure(0, weight=1)
        log_card.grid_rowconfigure(1, weight=1)

        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 6))
        ctk.CTkLabel(log_header, text="Live UART Log", font=("Segoe UI Semibold", 13),
                     text_color=COLORS["text_bright"]).pack(side="left")

        self.log_box = ctk.CTkTextbox(log_card, font=("Consolas", 12),
                                       fg_color=COLORS["console_bg"],
                                       text_color="#c7e6c9", corner_radius=8,
                                       border_width=0)
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))

        # ---- Local analysis results (card) ----
        result_card = ctk.CTkFrame(content, fg_color=COLORS["card"], corner_radius=12,
                                    border_width=1, border_color=COLORS["card_border"])
        result_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        result_card.grid_columnconfigure(0, weight=1)
        result_card.grid_rowconfigure(1, weight=1)

        result_header = ctk.CTkFrame(result_card, fg_color="transparent")
        result_header.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 6))
        ctk.CTkLabel(result_header, text="Local Analysis Results", font=("Segoe UI Semibold", 13),
                     text_color=COLORS["text_bright"]).pack(side="left")

        self.result_box = ctk.CTkTextbox(result_card, font=("Consolas", 12),
                                          fg_color=COLORS["console_bg"],
                                          text_color=COLORS["text_bright"], corner_radius=8,
                                          border_width=0)
        self.result_box.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))

    # ---- Footer status bar --------------------------------------------
    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=0, height=30)
        footer.grid(row=3, column=0, sticky="ew")
        footer.grid_propagate(False)
        ctk.CTkLabel(footer, text=f"Logs saved to: {config.LOGS_DIR}",
                     font=("Segoe UI", 10), text_color=COLORS["text_dim"]
                     ).pack(side="left", padx=16, pady=6)

    # ------------------------------------------------------------------
    # Status helper (updates both dot color and text together)
    # ------------------------------------------------------------------
    def _set_status(self, text, color_key):
        color = COLORS.get(color_key, COLORS["text_dim"])
        self.status_dot.configure(text_color=color)
        self.status_label.configure(text=text, text_color=color)

    # ------------------------------------------------------------------
    # Port handling
    # ------------------------------------------------------------------
    def _refresh_ports(self):
        ports = list_available_ports()
        values = [f"{p['device']} - {p['description']}" for p in ports]
        self.port_dropdown.configure(values=values)
        if values:
            self.port_dropdown.set(values[0])
        else:
            self.port_dropdown.set("No ports found")

    def _get_selected_port(self):
        selected = self.port_dropdown.get()
        if not selected or "No ports" in selected:
            return None
        return selected.split(" - ")[0]  # "COM5 - USB CH340" -> "COM5"

    def _get_selected_baud(self):
        selected = self.baud_dropdown.get()
        return int(selected.split(" ")[0])  # "921600 (MediaTek...)" -> 921600

    # ------------------------------------------------------------------
    # Capture controls
    # ------------------------------------------------------------------
    def _on_start_clicked(self):
        port = self._get_selected_port()
        if not port:
            messagebox.showwarning("Port Missing", "Koi COM port select nahi hai. "
                                    "Adapter connect karke Refresh (⟳) dabao.")
            return

        baud = self._get_selected_baud()

        self.log_box.delete("1.0", "end")
        self.result_box.delete("1.0", "end")
        self.current_log_text = ""

        self.reader = UartReader(
            port=port,
            baud_rate=baud,
            on_line=self._append_log_line,     # har naye line pe UI update
            on_finish=self._on_capture_finished,
            on_error=self._on_capture_error,
        )
        self.reader.start(duration_seconds=config.DEFAULT_CAPTURE_DURATION)

        self.start_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self._set_status("Capturing...", "success")

    def _on_stop_clicked(self):
        if self.reader:
            self.reader.stop()
        self._set_status("Stopping...", "warning")

    # ------------------------------------------------------------------
    # Callbacks (ye background thread se call hote hain, isliye `after`
    # use karke safely main UI thread par schedule karte hain)
    # ------------------------------------------------------------------
    def _append_log_line(self, line):
        self.after(0, self._append_log_line_ui, line)

    def _append_log_line_ui(self, line):
        self.log_box.insert("end", line + "\n")
        self.log_box.see("end")  # auto-scroll niche

    def _on_capture_finished(self, full_log):
        self.after(0, self._on_capture_finished_ui, full_log)

    def _on_capture_finished_ui(self, full_log):
        self.current_log_text = full_log
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

        if len(full_log.strip()) < config.MIN_VALID_LOG_LENGTH:
            self._set_status("No/very little data -- check wiring (TX/RX/GND)", "danger")
            return

        # Auto-save
        model = self.model_entry.get().strip() or "unknown"
        filepath = save_log_to_file(full_log, config.LOGS_DIR, phone_model=model)
        self._set_status(f"Saved → {filepath}", "success")

        # Auto-run local analysis bhi kar do
        self._run_local_analysis()

    def _on_capture_error(self, error_message):
        self.after(0, self._on_capture_error_ui, error_message)

    def _on_capture_error_ui(self, error_message):
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self._set_status("Error", "danger")
        messagebox.showerror("UART Error", error_message)

    # ------------------------------------------------------------------
    # Analysis + AI prompt
    # ------------------------------------------------------------------
    def _on_analyze_clicked(self):
        if not self.current_log_text:
            messagebox.showinfo("No Log", "Pehle 'Start Capture' se koi log capture karo.")
            return
        self._run_local_analysis()

    def _run_local_analysis(self):
        findings = run_local_analysis(self.current_log_text)
        summary = format_local_analysis_summary(findings)

        self.result_box.delete("1.0", "end")
        self.result_box.insert("1.0", summary)

        # AI prompt bhi tayaar rakh lo (findings ke sath, taaki AI ko extra context mile)
        model = self.model_entry.get().strip()
        self.last_ai_prompt = build_ai_prompt(self.current_log_text, phone_model=model,
                                               local_findings=findings)

    def _on_copy_ai_clicked(self):
        if not self.current_log_text:
            messagebox.showinfo("No Log", "Pehle 'Start Capture' se koi log capture karo.")
            return

        if not self.last_ai_prompt:
            # Agar local analysis abhi tak nahi chala to bina findings ke prompt bana do
            model = self.model_entry.get().strip()
            self.last_ai_prompt = build_ai_prompt(self.current_log_text, phone_model=model)

        pyperclip.copy(self.last_ai_prompt)
        messagebox.showinfo("Copied!", "AI prompt clipboard mein copy ho gaya hai.\n"
                             "Ab isse kisi bhi AI chat (Claude/ChatGPT) mein paste karo.")