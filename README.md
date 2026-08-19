<div align="center">

# ⚡ Mobile UART Analyzer

### Professional Hardware Diagnostics Tool for Mobile Phone Repair Technicians

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/yourusername/mobile-uart-analyzer)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)](https://github.com/yourusername/mobile-uart-analyzer)

**Real-time UART log capture • Multi-platform chipset support • AI-ready diagnostics**

[Features](#-features) • [Installation](#-installation) • [Usage](#-usage-guide) • [Architecture](#-architecture) • [Contributing](#-contributing)

</div>

---

## 🎯 What is Mobile UART Analyzer?

Mobile UART Analyzer is a specialized diagnostic tool designed for mobile phone repair technicians to capture and analyze boot logs from smartphone motherboards via UART (Universal Asynchronous Receiver-Transmitter) connections. It automatically detects hardware faults, identifies stuck boot stages, and provides actionable repair guidance—saving hours of manual troubleshooting.

### 🔥 Why This Tool?

When a phone won't boot, traditional diagnostic methods fall short. This tool:
- **Captures live boot logs** directly from the motherboard's UART pins
- **Automatically identifies faults** using pattern recognition, boot-loop detection, and firmware-level log parsing
- **Provides voltage rail checklists** for precise multimeter measurements
- **Generates AI-ready prompts** for deeper analysis with Claude/ChatGPT
- **Supports multiple chipsets**: Qualcomm, MediaTek (MTK), Spreadtrum, and legacy platforms

---

## ✨ Features

### 🔌 Hardware Interface
- **Real-time UART capture** with live log streaming
- **Auto-detection** of available COM/serial ports
- **Multi-baud rate support** with chipset-specific presets:
  - 115200 (Common/Default)
  - 921600 (MediaTek boards)
  - 460800 (Qualcomm boards)
  - 230400 (Spreadtrum boards)
  - 38400 (Older/legacy devices)
- **Configurable capture duration** with manual stop control

### 🧠 Intelligent Analysis Engine

#### 1️⃣ **Keyword-Based Fault Detection**
Scans logs against a comprehensive database of known hardware fault signatures:
- **Storage failures** (eMMC/UFS initialization errors)
- **Power issues** (PMIC failures, power sequence faults)
- **Bootloader corruption** (preloader, fastboot, dm-verity issues)
- **Boot loops** (watchdog resets, reboot cycles)
- **Communication faults** (modem, RF calibration)

#### 2️⃣ **Algorithmic Boot-Loop Detection**
Goes beyond simple keyword matching:
- **Pattern recognition** that identifies repeating log blocks
- **Confidence scoring** based on block size and repetition count
- **Subsystem diversity analysis** to filter out false positives
- **Auto-detects** even when keywords are absent

#### 3️⃣ **Qualcomm SBL Log Parser** 🎖️
Decodes Qualcomm's official Secondary Boot Loader (SBL) log format:
- **Reads firmware structure** (B/D/S log types with timestamps)
- **Identifies exact stuck stages** by finding started-but-never-completed boot phases
- **Extracts error codes** with source file and line number
- **Subsystem mapping** (DDR/RAM, Storage, PMIC, Secure Boot, etc.)
- **Safe for non-Qualcomm logs** (auto-detects format and returns empty for MediaTek/others)

#### 4️⃣ **Voltage Rail Reference Database**
Provides multimeter-ready checklists when memory/storage faults are detected:
- **LPDDR3/LPDDR4/LPDDR4X** voltage rails (VDD1, VDD2, VDDQ, VREF)
- **eMMC and UFS** power supplies (VCC, VCCQ, VCCQ2)
- **Generic + board-specific** values (extensible knowledge base)
- **Measurement hints** for each rail

### 🎨 Modern User Interface
- **Dark-themed** professional design built with CustomTkinter
- **Responsive layout** with resizable log console and results panel
- **Real-time status indicators** (Idle/Capturing/Error with color coding)
- **Compact controls** maximizing screen space for logs
- **One-click AI prompt generation** with clipboard copy

### 📦 Export & Integration
- **Auto-saves** all captured logs with timestamps and phone model
- **AI-ready prompts** structured for Claude/ChatGPT analysis
- **Plain-text logs** for archival and sharing

### ⚙️ CI/CD & Distribution
- **GitHub Actions** workflow for automated Windows EXE builds
- **PyInstaller** packaging for standalone executables
- **Tag-based releases** (push `v1.0.0` → auto-build → GitHub Release)

---

## 📁 Project Structure

```
mobile-uart-analyzer/
│
├── 📂 core/                          # Analysis engine & hardware interface
│   ├── analyzer.py                   # Main analysis orchestrator
│   ├── uart_reader.py                # Serial port communication (pyserial)
│   ├── fault_patterns.py             # Fault signature database
│   ├── boot_loop_detector.py         # Algorithmic boot-loop detection
│   ├── qualcomm_sbl_parser.py        # Qualcomm SBL log parser
│   └── voltage_rails.py              # Voltage rail reference database
│
├── 📂 ui/                            # User interface
│   └── app_window.py                 # Main GUI (CustomTkinter)
│
├── 📂 .github/workflows/             # CI/CD automation
│   └── build.yml                     # Windows EXE build workflow
│
├── 📂 logs/                          # Auto-saved capture logs
├── 📂 assets/                        # UI assets (icons, images)
│
├── config.py                         # Centralized configuration
├── main.py                           # Application entry point
├── requirements.txt                  # Python dependencies
├── LICENSE                           # MIT License
└── README.md                         # You are here 📍
```

---

## 🚀 Installation

### Prerequisites
- **Python 3.11+** ([Download here](https://www.python.org/downloads/))
- **USB-to-UART adapter** (CH340, CP2102, FTDI, etc.)
- **USB drivers** for your adapter ([CH340 drivers](http://www.wch-ic.com/downloads/CH341SER_ZIP.html))

### Option 1: Run from Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/yourusername/mobile-uart-analyzer.git
cd mobile-uart-analyzer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Option 2: Windows Executable (No Python Required)

1. Download the latest `MobileUartAnalyzer.exe` from [Releases](https://github.com/yourusername/mobile-uart-analyzer/releases)
2. Double-click to run (no installation needed)

### Dependencies

```
pyserial       # Serial port communication
customtkinter  # Modern UI framework
pyperclip      # Clipboard operations
Pillow         # Image handling (for future UI enhancements)
```

---

## 📖 Usage Guide

### 1️⃣ Hardware Setup

#### Required Hardware:
- Mobile phone motherboard with exposed UART test points
- USB-to-TTL/UART adapter (3.3V logic level)
- Jumper wires

#### Wiring:
```
Phone Board          USB-UART Adapter
-----------          ----------------
   TX       ────────>     RX
   RX       <────────     TX
   GND      ────────>     GND
```

⚠️ **Important:**
- **Do NOT connect VCC** (phone should be powered separately)
- **Use 3.3V logic level** adapters (5V may damage the board)
- **Ensure proper grounding** (GND connection is critical)

### 2️⃣ Software Workflow

#### Step 1: Connect Hardware
1. Connect USB-UART adapter to your computer
2. Launch Mobile UART Analyzer
3. Click **Refresh (⟳)** to detect the COM port

#### Step 2: Configure Settings
- **Port**: Select your adapter's COM port (e.g., COM5)
- **Baud Rate**: Choose based on chipset:
  - MediaTek → 921600
  - Qualcomm → 460800
  - Unknown → Start with 115200
- **Phone Model**: Enter phone model (optional, helps with analysis)

#### Step 3: Capture Boot Log
1. Click **▶ Start Capture**
2. Power on the phone (or trigger a reboot)
3. Logs will stream in real-time (left panel)
4. Click **■ Stop** manually or wait for auto-stop (default: 2 minutes)

#### Step 4: Analyze Results
- **Local Analysis Results** appear automatically (right panel)
- Review detected faults, boot-loop patterns, and voltage checklists
- Click **📋 Copy AI Prompt** to generate a structured prompt for Claude/ChatGPT

#### Step 5: Advanced Diagnosis
Paste the AI prompt into an LLM for deeper analysis:
```
Claude/ChatGPT will provide:
✓ Exact boot stage failure point
✓ Root cause hypothesis
✓ Step-by-step repair guidance
✓ Confidence level assessment
```

### 3️⃣ Understanding Analysis Results

#### Example Output:
```
[Storage (eMMC)] Keyword: 'emmc init fail'
  -> eMMC initialize nahi ho paya. Reball/replace check karo.
  Matched lines (5 shown):
     [PLFM] emmc init fail, error code: 0x8001
     [PLFM] mmc0: timeout waiting for card ready
     ...

[CPU / Boot Loop] Confidence: High
  -> 7-line block 4x repeat hua -- chip kisi stage pe atak kar
     baar-baar restart ho rahi hai.

========================================
VOLTAGE-RAIL CHECKLIST
========================================
[eMMC] Generic reference rails:
   VCC: ~2.9V or 3.3V -- Main power supply
      Hint: Measure directly on eMMC chip's VCC pins/pads
   VCCQ: ~1.8V -- I/O supply
      Hint: Missing VCCQ often causes eMMC to be undetected
```

---

## 🛠️ Architecture

### Core Components

#### **analyzer.py** - Analysis Orchestrator
Central hub that coordinates all analysis modules:
- `run_local_analysis()` - Runs fault pattern matching + boot-loop detection
- `get_voltage_rail_summary()` - Generates voltage checklists
- `get_qualcomm_sbl_summary()` - Parses Qualcomm firmware logs
- `build_ai_prompt()` - Creates LLM-ready diagnostic prompts

#### **uart_reader.py** - Hardware Interface
Handles serial communication:
- Background thread for non-blocking capture
- Auto-reconnection and error handling
- Timestamped log file saving
- Configurable timeout and duration

#### **fault_patterns.py** - Knowledge Base
Database of ~15 known fault signatures across:
- Storage (eMMC/UFS errors)
- Power (PMIC failures)
- Bootloader (corruption, security)
- CPU (watchdog, boot loops)
- Connectivity (modem, RF)

#### **boot_loop_detector.py** - Pattern Recognition
Algorithmic detection using:
- Sliding window block comparison
- Non-overlapping repetition counting
- Subsystem diversity filtering
- Confidence scoring (High/Medium)

#### **qualcomm_sbl_parser.py** - Firmware Log Parser
Parses Qualcomm's structured boot logs:
- Extracts `B` (Start), `D` (Delta/Complete), `S` (Static) log types
- Identifies stuck stages (Start without matching Delta)
- Decodes error codes with source file/line mapping
- Maps source files to subsystems (DDR, Storage, PMIC, etc.)

#### **voltage_rails.py** - Reference Database
Generic + board-specific voltage values:
- LPDDR3/4/4X RAM rails (VDD1, VDD2, VDDQ)
- eMMC/UFS storage rails (VCC, VCCQ)
- Extensible for verified board-specific measurements

### Data Flow

```
User Action (Start Capture)
       ↓
[uart_reader.py] Opens serial port, reads lines in background thread
       ↓
[app_window.py] Displays live log in UI console
       ↓
User Action (Stop / Auto-timeout)
       ↓
[analyzer.py] Orchestrates analysis:
  ├─→ [fault_patterns.py] Keyword scan
  ├─→ [boot_loop_detector.py] Algorithmic pattern detection
  ├─→ [qualcomm_sbl_parser.py] Firmware log parsing (if Qualcomm)
  └─→ [voltage_rails.py] Checklist generation (if storage fault)
       ↓
[app_window.py] Displays results + generates AI prompt
       ↓
User copies prompt → Pastes into Claude/ChatGPT → Gets detailed diagnosis
```

---

## 🔧 Configuration

Edit `config.py` to customize:

```python
# App branding
APP_NAME = "Mobile UART Analyzer"
APP_VERSION = "1.0.0"

# Default capture settings
DEFAULT_BAUD_RATE = 115200
DEFAULT_CAPTURE_DURATION = 120  # seconds

# Baud rate presets (add your own)
BAUD_RATE_OPTIONS = [
    ("115200", "Common / Default"),
    ("921600", "MediaTek"),
    # Add custom rates here
]

# UI theme
UI_APPEARANCE_MODE = "dark"  # "dark" | "light" | "system"
UI_COLOR_THEME = "blue"
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### 🐛 Bug Reports
Open an issue with:
- Your OS and Python version
- Steps to reproduce
- Log file (if applicable)

### 💡 Feature Requests
Suggest new features:
- Additional chipset support
- New fault patterns
- UI improvements

### 📝 Code Contributions

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit changes: `git commit -m 'Add your feature'`
4. Push to branch: `git push origin feature/your-feature`
5. Open a Pull Request

### 🔬 Expanding the Knowledge Base

**Voltage Rails** (`core/voltage_rails.py`):
```python
BOARD_SPECIFIC_OVERRIDES = {
    "Redmi Note 10 (MT6768)": {
        "memory_type": "LPDDR4",
        "verified_rails": {"VDD2": "1.125V"},
        "notes": "Confirmed via multimeter, 2026-08-20",
    },
}
```

**Fault Patterns** (`core/fault_patterns.py`):
```python
FAULT_PATTERNS.append({
    "keyword": "your_error_keyword",
    "category": "Category Name",
    "hint": "Repair guidance here",
})
```

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License - Copyright (c) 2026

Permission is granted to use, modify, and distribute this software.
Provided "AS IS" without warranty. See LICENSE for full terms.
```

---

## 👨‍💻 Credits

**Developed by:** Riaz Ahmed  
**Architecture:** Modular Python design with separation of concerns  
**UI Framework:** [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) by Tom Schimansky  
**Hardware Interface:** [PySerial](https://github.com/pyserial/pyserial)  

### Special Thanks
- Mobile repair community for fault pattern contributions
- Qualcomm's public documentation for SBL log format specifications
- Open-source contributors to pyserial, CustomTkinter, and Python ecosystem

---

## 📞 Support

### Documentation
- [Qualcomm Boot Flow](https://developer.qualcomm.com/qfile/33561/lm80-p0436-1_little_kernel_boot_loader_overview.pdf) (Official Qualcomm guide)
- [UART Basics for Mobile Repair](https://www.gsmforum.com/uart-boot-log-guide/)

### Community
- Open an [Issue](https://github.com/yourusername/mobile-uart-analyzer/issues) for bugs/questions
- Join [Telegram/Discord](#) for real-time support (coming soon)

### Commercial Support
For training, custom features, or board-specific validation services, contact: [your-email@example.com]

---

## 🎯 Roadmap

### Planned Features
- [ ] **MediaTek log parser** (similar to Qualcomm SBL parser)
- [ ] **Screenshot capture** of live logs during capture
- [ ] **Log comparison tool** (diff between working/faulty boards)
- [ ] **Export to PDF** with annotated findings
- [ ] **Remote AI analysis** (built-in Claude API integration)
- [ ] **Board database** with pinouts and reference voltages
- [ ] **Multi-language UI** (Urdu, Hindi, Arabic)
- [ ] **Mobile app** (Android) for on-the-go diagnostics

### Version History
- **v1.0.0** (2026-08) - Initial release with Qualcomm SBL parser, boot-loop detector, voltage rails

---

## ⚠️ Disclaimer

This tool is designed for **professional technicians** working on hardware they own or have authorization to repair. 

- **No warranties** provided - verify all voltage measurements with datasheets
- **UART connections** can damage boards if done incorrectly (use 3.3V logic levels)
- **Generic voltage values** are reference guides, not guaranteed for every board
- **AI-generated diagnoses** are suggestions, not definitive—always confirm with testing

**USE AT YOUR OWN RISK.** The authors are not liable for hardware damage or data loss.

---

<div align="center">

### ⚡ Built for technicians, by technicians

**Star ⭐ this repo if it helped you fix a phone!**

[Report Bug](https://github.com/yourusername/mobile-uart-analyzer/issues) • [Request Feature](https://github.com/yourusername/mobile-uart-analyzer/issues) • [Discussions](https://github.com/yourusername/mobile-uart-analyzer/discussions)

---

Made with ⚡ and ❤️ for the mobile repair community

</div>
