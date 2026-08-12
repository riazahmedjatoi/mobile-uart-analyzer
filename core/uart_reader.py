import threading
import time
from datetime import datetime

import serial
import serial.tools.list_ports


def list_available_ports():
    """
    System mein connected saare serial/COM ports ki list deta hai.
    Har entry ek dict hai: {"device": "COM5", "description": "USB-SERIAL CH340"}
    """
    ports = []
    for p in serial.tools.list_ports.comports():
        ports.append({
            "device": p.device,
            "description": p.description or "Unknown device",
        })
    return ports


class UartReader:
    """
    UART se data capture karne wali class.

    Usage:
        reader = UartReader(
            port="COM5",
            baud_rate=921600,
            on_line=lambda line: print(line),       # har naye line pe callback
            on_finish=lambda full_log: print("done"),  # capture khatam hone par
        )
        reader.start(duration_seconds=120)
        ...
        reader.stop()   # zaroorat pade to manually rok sakte ho
    """

    def __init__(self, port, baud_rate, on_line=None, on_finish=None, on_error=None):
        self.port = port
        self.baud_rate = int(baud_rate)
        self.on_line = on_line          # callback: (str) -> None, har line ke liye
        self.on_finish = on_finish      # callback: (str) -> None, poora log milne par
        self.on_error = on_error        # callback: (str) -> None, error hone par

        self._serial_conn = None
        self._thread = None
        self._stop_flag = threading.Event()
        self._captured_lines = []

    # ------------------------------------------------------------------
    # Public controls
    # ------------------------------------------------------------------
    def start(self, duration_seconds=120):
        """Background thread mein capture shuru karta hai (non-blocking)."""
        self._stop_flag.clear()
        self._captured_lines = []
        self._thread = threading.Thread(
            target=self._capture_loop,
            args=(duration_seconds,),
            daemon=True,
        )
        self._thread.start()

    def stop(self):
        """Capture ko turant rok deta hai (user ne 'Stop' dabaya)."""
        self._stop_flag.set()

    def is_running(self):
        return self._thread is not None and self._thread.is_alive()

    # ------------------------------------------------------------------
    # Internal logic (background thread ke andar chalta hai)
    # ------------------------------------------------------------------
    def _capture_loop(self, duration_seconds):
        try:
            self._serial_conn = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=1,  # 1 sec tak wait karega agar data na aaye, phir loop check karega
            )
        except serial.SerialException as e:
            if self.on_error:
                self.on_error(f"Port open nahi ho saka ({self.port}): {e}")
            return

        start_time = time.time()

        try:
            while not self._stop_flag.is_set():
                # Time limit khatam ho gayi to capture rok do
                if time.time() - start_time > duration_seconds:
                    break

                try:
                    raw_line = self._serial_conn.readline()
                except serial.SerialException as e:
                    if self.on_error:
                        self.on_error(f"Read error: {e}")
                    break

                if not raw_line:
                    # timeout ho gaya, koi naya data nahi aaya -- loop continue karo
                    continue

                # Bytes ko text mein convert karo, corrupted bytes ko safely ignore karo
                decoded = raw_line.decode("utf-8", errors="ignore").rstrip("\r\n")
                if decoded:
                    self._captured_lines.append(decoded)
                    if self.on_line:
                        self.on_line(decoded)

        finally:
            if self._serial_conn and self._serial_conn.is_open:
                self._serial_conn.close()

        full_log = "\n".join(self._captured_lines)
        if self.on_finish:
            self.on_finish(full_log)

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------
    def get_captured_log(self):
        return "\n".join(self._captured_lines)


def save_log_to_file(log_text, logs_dir, phone_model="unknown"):
    """
    Log text ko ek timestamped .txt file mein save karta hai.
    Return karta hai saved file ka full path.
    """
    import os

    safe_model = "".join(c for c in phone_model if c.isalnum() or c in ("-", "_")) or "unknown"
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"boot_log_{safe_model}_{timestamp}.txt"
    filepath = os.path.join(logs_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(log_text)

    return filepath
