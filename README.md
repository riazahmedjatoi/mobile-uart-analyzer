# Mobile UART Analyzer

Free aur open-source UART boot-log capture tool for mobile repair technicians.
Cheap USB-to-UART adapter (CH340 / CH341 / CP2102 / FT232 / etc.) se mobile
motherboard connect karke boot logs capture karta hai, known faults ka quick
local check deta hai, aur ek ready-made AI prompt bana deta hai jise aap
kisi bhi AI chat (Claude, ChatGPT, etc.) mein paste karke detailed diagnosis
maang sakte ho.

**Ye tool khud kisi bhi AI se connect nahi hota** -- koi API key, koi
internet dependency nahi. Sab kuch 100% local chalta hai, sirf clipboard
copy se aap manually AI ko de sakte ho.

## Features

- Auto-detect available COM/serial ports
- Common baud-rate presets (MediaTek, Qualcomm, etc.)
- Live scrolling boot-log view
- Auto-save every capture as a timestamped `.txt` file
- Offline keyword-based fault hints (eMMC, PMIC, bootloader, boot-loop...)
- One-click "Copy AI Prompt" -- structured prompt clipboard mein copy ho jata hai

## Hardware Required

- Koi bhi USB-to-UART adapter: CH340 / CH341 / CH9102 / PL2303 / CP2102 / FT232
- Mobile motherboard ke TX / RX / GND test points tak wire/pogo-pin connection

## Installation

```bash
git clone https://github.com/your-username/mobile-uart-analyzer.git
cd mobile-uart-analyzer
pip install -r requirements.txt
python main.py
```

Requires Python 3.9+.

## Usage

1. Adapter ko board ke UART pins (TX, RX, GND) se connect karo, USB PC mein lagao
2. App kholo, "Refresh" dabao taaki port list update ho
3. Sahi COM port aur baud rate select karo (chipset ke hisaab se)
4. "Start Capture" dabao, phir phone ko boot karo
5. Log real-time mein screen pe dikhega, aur khatam hone par auto-save + local
   analysis chalega
6. Agar deeper analysis chahiye, "Copy AI Prompt" dabao aur kisi bhi AI chat
   mein paste kar do

## Adding new fault patterns

`core/fault_patterns.py` file kholo aur `FAULT_PATTERNS` list mein naya dict
add karo:

```python
{
    "keyword": "your keyword here",
    "category": "Storage / Power / Bootloader / etc.",
    "hint": "Technician ke liye chhota explanation",
},
```

Jitne zyada real-world patterns is list mein add hote jayenge, tool utna hi
zyada useful hota jayega -- bina kisi AI call ke bhi.

## Building a standalone .exe (optional)

Non-technical users (jaise field technicians) ke liye, PyInstaller se ek
single `.exe` bana sakte ho:

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name MobileUartAnalyzer main.py
```

Output `dist/MobileUartAnalyzer.exe` mein milega -- ise GitHub "Releases"
section mein upload kar do.

## Disclaimer

Ye tool sirf UART logs read/save/analyze karta hai. Ye har fault detect
nahi kar sakta -- kai hardware issues UART log mein dikhte hi nahi. Final
diagnosis aur repair decision technician ki apni knowledge aur judgement par
depend karta hai.

## License

MIT License -- dekho `LICENSE` file.
