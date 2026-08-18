"""
ui/app_window.py
------------------
Poora GUI is file mein hai. customtkinter use kiya hai (modern, dark-theme
tkinter wrapper). Ye file sirf "display + button clicks" handle karti hai --
actual hardware/analysis logic core/ folder ki files mein hai.

Layout (responsive, grid-based, compact):

    ┌─────────────────────────────────────────────────────────┐
    │  HEADER (thin)                                            │
    ├─────────────────────────────────────────────────────────┤
    │  CONNECTION CARD (thin)                                    │
    ├───────────────────────────┬───────────────────────────────┤
    │  LIVE LOG CONSOLE          │  LOCAL ANALYSIS RESULTS         │
    │  (max area, resizable)     │  (max area, resizable)           │
    └───────────────────────────┴───────────────────────────────┘
    │  FOOTER (thin)                                               │
    └─────────────────────────────────────────────────────────┘
"""

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk
import pyperclip

import config
from core.uart_reader import UartReader, list_available_ports, save_log_to_file
from core.analyzer import run_local_analysis, format_local_analysis_summary, build_ai_prompt


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
        self.minsize(880, 560)
        self.configure(fg_color=COLORS["bg"])

        self.reader = None
        self.current_log_text = ""
        self.last_ai_prompt = ""

        self._build_layout()
        self._refresh_ports()

    def _build_layout(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._build_header()
        self._build_connection_card()
        self._build_main_content()
        self._build_footer()

    # ---- Header (compact) ----------------------------------------------
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=0,
                               border_width=0, height=40)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        logo_dot = ctk.CTkFrame(header, fg_color=COLORS["accent"], corner_radius=6,
                                 width=24, height=24)
        logo_dot.grid(row=0, column=0, padx=(10, 8), pady=8)
        logo_dot.grid_propagate(False)
        ctk.CTkLabel(logo_dot, text="⚡", font=("Segoe UI", 11), text_color="white").place(
            relx=0.5, rely=0.5, anchor="center")

        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="w", pady=4)
        title_row = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_row.pack(anchor="w")
        ctk.CTkLabel(title_row, text=config.APP_NAME,
                     font=("Segoe UI Semibold", 13), text_color=COLORS["text_bright"]
                     ).pack(side="left")
        ctk.CTkLabel(title_row, text=f"  v{config.APP_VERSION}",
                     font=("Segoe UI", 10), text_color=COLORS["text_dim"]
                     ).pack(side="left")

        owner_label = ctk.CTkLabel(header, text="Riaz Ahmed",
                                    font=("Segoe UI", 10), text_color=COLORS["text_dim"])
        owner_label.grid(row=0, column=2, padx=(0, 14), sticky="e")

        status_wrap = ctk.CTkFrame(header, fg_color="transparent")
        status_wrap.grid(row=0, column=3, padx=(0, 14), sticky="e")

        self.status_dot = ctk.CTkLabel(status_wrap, text="●", font=("Segoe UI", 11),
                                        text_color=COLORS["text_dim"])
        self.status_dot.pack(side="left", padx=(0, 5))
        self.status_label = ctk.CTkLabel(status_wrap, text="Idle",
                                          font=("Segoe UI", 10), text_color=COLORS["text_dim"])
        self.status_label.pack(side="left")

    # ---- Connection / controls card (compact) --------------------------
    def _build_connection_card(self):
        card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=8,
                             border_width=1, border_color=COLORS["card_border"])
        card.grid(row=1, column=0, sticky="ew", padx=8, pady=(6, 4))

        for col in (1, 3, 5):
            card.grid_columnconfigure(col, weight=1)

        pad = {"padx": (4, 10), "pady": 6}

        ctk.CTkLabel(card, text="Port", font=("Segoe UI", 10),
                     text_color=COLORS["text_dim"]).grid(row=0, column=0, sticky="w", padx=(10, 4))
        self.port_dropdown = ctk.CTkComboBox(card, values=[], width=160, height=26,
                                              font=("Segoe UI", 11),
                                              border_color=COLORS["card_border"])
        self.port_dropdown.grid(row=0, column=1, sticky="ew", **pad)

        refresh_btn = ctk.CTkButton(card, text="⟳", width=28, height=26,
                                     fg_color=COLORS["card_border"],
                                     hover_color=COLORS["accent"], command=self._refresh_ports)
        refresh_btn.grid(row=0, column=2, padx=(0, 10), pady=6)

        ctk.CTkLabel(card, text="Baud Rate", font=("Segoe UI", 10),
                     text_color=COLORS["text_dim"]).grid(row=0, column=3, sticky="w", padx=(0, 4))
        baud_values = [f"{rate} ({label})" for rate, label in config.BAUD_RATE_OPTIONS]
        self.baud_dropdown = ctk.CTkComboBox(card, values=baud_values, width=200, height=26,
                                              font=("Segoe UI", 11),
                                              border_color=COLORS["card_border"])
        self.baud_dropdown.set(baud_values[0])
        self.baud_dropdown.grid(row=0, column=4, sticky="ew", **pad)

        ctk.CTkLabel(card, text="Phone Model", font=("Segoe UI", 10),
                     text_color=COLORS["text_dim"]).grid(row=0, column=5, sticky="w", padx=(0, 4))
        self.model_entry = ctk.CTkEntry(card, width=150, height=26, font=("Segoe UI", 11),
                                         placeholder_text="e.g. Redmi Note 10",
                                         border_color=COLORS["card_border"])
        self.model_entry.grid(row=0, column=6, sticky="ew", padx=(4, 10), pady=6)

        action_row = ctk.CTkFrame(card, fg_color="transparent")
        action_row.grid(row=1, column=0, columnspan=7, sticky="ew", padx=10, pady=(0, 8))

        self.start_btn = ctk.CTkButton(
            action_row, text="▶  Start Capture", height=28, corner_radius=6,
            fg_color=COLORS["success"], hover_color=COLORS["success_hover"],
            font=("Segoe UI Semibold", 11), command=self._on_start_clicked)
        self.start_btn.pack(side="left", padx=(0, 6))

        self.stop_btn = ctk.CTkButton(
            action_row, text="■  Stop", height=28, corner_radius=6,
            fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
            font=("Segoe UI Semibold", 11), command=self._on_stop_clicked, state="disabled")
        self.stop_btn.pack(side="left", padx=6)

        self.analyze_btn = ctk.CTkButton(
            action_row, text="🔍  Run Local Analysis", height=28, corner_radius=6,
            fg_color=COLORS["card_border"], hover_color=COLORS["accent"],
            font=("Segoe UI", 11), command=self._on_analyze_clicked)
        self.analyze_btn.pack(side="left", padx=6)

        self.copy_ai_btn = ctk.CTkButton(
            action_row, text="📋  Copy AI Prompt", height=28, corner_radius=6,
            fg_color=COLORS["card_border"], hover_color=COLORS["accent"],
            font=("Segoe UI", 11), command=self._on_copy_ai_clicked)
        self.copy_ai_btn.pack(side="left", padx=6)

    # ---- Main content: log console (left) + results (right) -----------
    def _build_main_content(self):
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=2, column=0, sticky="nsew", padx=8, pady=(0, 4))

        content.grid_columnconfigure(0, weight=3)
        content.grid_columnconfigure(1, weight=2)
        content.grid_rowconfigure(0, weight=1)

        log_card = ctk.CTkFrame(content, fg_color=COLORS["card"], corner_radius=8,
                                 border_width=1, border_color=COLORS["card_border"])
        log_card.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        log_card.grid_columnconfigure(0, weight=1)
        log_card.grid_rowconfigure(1, weight=1)

        log_header = ctk.CTkFrame(log_card, fg_color="transparent")
        log_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 4))
        ctk.CTkLabel(log_header, text="Live UART Log", font=("Segoe UI Semibold", 11),
                     text_color=COLORS["text_bright"]).pack(side="left")

        self.log_box = ctk.CTkTextbox(log_card, font=("Consolas", 12),
                                       fg_color=COLORS["console_bg"],
                                       text_color="#c7e6c9", corner_radius=4,
                                       border_width=0)
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))

        result_card = ctk.CTkFrame(content, fg_color=COLORS["card"], corner_radius=8,
                                    border_width=1, border_color=COLORS["card_border"])
        result_card.grid(row=0, column=1, sticky="nsew", padx=(4, 0))
        result_card.grid_columnconfigure(0, weight=1)
        result_card.grid_rowconfigure(1, weight=1)

        result_header = ctk.CTkFrame(result_card, fg_color="transparent")
        result_header.grid(row=0, column=0, sticky="ew", padx=10, pady=(6, 4))
        ctk.CTkLabel(result_header, text="Local Analysis Results", font=("Segoe UI Semibold", 11),
                     text_color=COLORS["text_bright"]).pack(side="left")

        self.result_box = ctk.CTkTextbox(result_card, font=("Consolas", 12),
                                          fg_color=COLORS["console_bg"],
                                          text_color=COLORS["text_bright"], corner_radius=4,
                                          border_width=0)
        self.result_box.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))

    # ---- Footer status bar (compact) ------------------------------------
    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=0, height=20)
        footer.grid(row=3, column=0, sticky="ew")
        footer.grid_propagate(False)
        ctk.CTkLabel(footer, text=f"Logs saved to: {config.LOGS_DIR}",
                     font=("Segoe UI", 9), text_color=COLORS["text_dim"]
                     ).pack(side="left", padx=10, pady=2)

    def _set_status(self, text, color_key):
        color = COLORS.get(color_key, COLORS["text_dim"])
        self.status_dot.configure(text_color=color)
        self.status_label.configure(text=text, text_color=color)

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
        return selected.split(" - ")[0]

    def _get_selected_baud(self):
        selected = self.baud_dropdown.get()
        return int(selected.split(" ")[0])

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
            on_line=self._append_log_line,
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

    def _append_log_line(self, line):
        self.after(0, self._append_log_line_ui, line)

    def _append_log_line_ui(self, line):
        self.log_box.insert("end", line + "\n")
        self.log_box.see("end")

    def _on_capture_finished(self, full_log):
        self.after(0, self._on_capture_finished_ui, full_log)

    def _on_capture_finished_ui(self, full_log):
        self.current_log_text = full_log
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")

        if len(full_log.strip()) < config.MIN_VALID_LOG_LENGTH:
            self._set_status("No/very little data -- check wiring (TX/RX/GND)", "danger")
            return

        model = self.model_entry.get().strip() or "unknown"
        filepath = save_log_to_file(full_log, config.LOGS_DIR, phone_model=model)
        self._set_status(f"Saved → {filepath}", "success")

        self._run_local_analysis()

    def _on_capture_error(self, error_message):
        self.after(0, self._on_capture_error_ui, error_message)

    def _on_capture_error_ui(self, error_message):
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self._set_status("Error", "danger")
        messagebox.showerror("UART Error", error_message)

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

        model = self.model_entry.get().strip()
        self.last_ai_prompt = build_ai_prompt(self.current_log_text, phone_model=model,
                                               local_findings=findings)

    def _on_copy_ai_clicked(self):
        if not self.current_log_text:
            messagebox.showinfo("No Log", "Pehle 'Start Capture' se koi log capture karo.")
            return

        if not self.last_ai_prompt:
            model = self.model_entry.get().strip()
            self.last_ai_prompt = build_ai_prompt(self.current_log_text, phone_model=model)

        pyperclip.copy(self.last_ai_prompt)
        messagebox.showinfo("Copied!", "AI prompt clipboard mein copy ho gaya hai.\n"
                             "Ab isse kisi bhi AI chat (Claude/ChatGPT) mein paste karo.")