"""
config.py
---------
Saari app-wide settings ek jagah. Kuch bhi default value change karni ho
(baud rate list, log folder, capture duration) to sirf yahi file edit karo.
"""

import os

# ---------------------------------------------------------------------------
# App info
# ---------------------------------------------------------------------------
APP_NAME = "Mobile UART Analyzer"
APP_VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Make sure the logs folder always exists (created automatically on first run)
os.makedirs(LOGS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Serial / UART settings
# ---------------------------------------------------------------------------
# Common baud rates used across different chipset platforms.
# Label batata hai kis platform pe generally kaunsa baud rate milta hai --
# ye sirf ek helpful hint hai, exact value board/chip pe depend karti hai.
BAUD_RATE_OPTIONS = [
    ("115200", "Common / Feature Phones / Default"),
    ("921600", "MediaTek (MTK) Boards"),
    ("460800", "Qualcomm (QCOM) Boards"),
    ("230400", "Some Spreadtrum Boards"),
    ("38400", "Older / Legacy Boards"),
]

DEFAULT_BAUD_RATE = 115200

# Kitni der tak log capture karna hai (seconds). User "Stop" bhi kabhi bhi
# dabaa sakta hai, ye sirf max safety-limit hai.
DEFAULT_CAPTURE_DURATION = 120

# Agar capture ke baad log itne characters se bhi chhota ho, to iska matlab
# UART se kuch data hi nahi mila (galat wiring / galat baud rate).
MIN_VALID_LOG_LENGTH = 20

# ---------------------------------------------------------------------------
# UI settings
# ---------------------------------------------------------------------------
UI_APPEARANCE_MODE = "dark"      # "dark" | "light" | "system"
UI_COLOR_THEME = "blue"          # customtkinter built-in theme
UI_WINDOW_SIZE = "1000x650"
