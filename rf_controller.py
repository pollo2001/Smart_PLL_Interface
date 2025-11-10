Python 3.12.2 (v3.12.2:6abddd9f6a, Feb  6 2024, 17:02:06) [Clang 13.0.0 (clang-1300.0.29.30)] on darwin
Type "help", "copyright", "credits" or "license()" for more information.
>>> """
... Smart_RF_Interface - Real-Time Controller Module
... ------------------------------------------------
... This module manages communication and synchronization between
... the GUI and an external RF device. All vendor-specific logic,
... commands, and identifiers have been removed to comply with NDA.
... 
... It demonstrates a complete communication abstraction layer,
... supporting:
...     • Automatic COM port detection and serial management
...     • Thread-safe command queue and non-blocking data exchange
...     • Periodic polling and sweep lifecycle control
...     • Clean shutdown and GUI synchronization
... """
... 
... import serial
... import threading
... import time
... import queue
... import sys
... import serial.tools.list_ports
... 
... 
... class RFController:
...     """
...     Core communication and control handler for a generic RF instrument.
...     Abstracts all serial I/O, sweep timing, and GUI callbacks.
...     """
... 
...     def __init__(self):
...         self.port = None
...         self.serial_handle = None
...         self.rx_queue = queue.Queue()
...         self.tx_queue = queue.Queue()
...         self.connected = False
...         self.polling_active = False
...         self._sweep_active = False
        self._stop_event = threading.Event()

        # Device identity placeholders
        self.device_id = "N/A"
        self.device_alias = "Generic RF Unit"

    # ---------------------------------------------------------------
    # Connection Management
    # ---------------------------------------------------------------

    def auto_connect(self, baudrate: int = 115200, timeout: float = 1.0):
        """Attempts to automatically detect and connect to the first available serial device."""
        try:
            ports = list(serial.tools.list_ports.comports())
            if not ports:
                print("[WARN] No COM ports detected. Manual connection required.")
                return False

            self.port = ports[0].device
            self.serial_handle = serial.Serial(
                self.port, baudrate, timeout=timeout, write_timeout=timeout
            )
            self.connected = True
            print(f"[INFO] Connected to {self.port}")
            return True
        except Exception as e:
            print(f"[ERROR] Connection failed: {e}")
            self.connected = False
            return False

    def disconnect(self):
        """Safely closes the serial connection and halts all threads."""
        self.polling_active = False
        self._sweep_active = False
        self._stop_event.set()
        try:
            if self.serial_handle and self.serial_handle.is_open:
                self.serial_handle.close()
            print("[INFO] Disconnected.")
        except Exception as e:
            print(f"[ERROR] Disconnection issue: {e}")
        finally:
            self.connected = False

    # ---------------------------------------------------------------
    # Command & Data Handling
    # ---------------------------------------------------------------

    def send_command(self, cmd: str):
        """
        Sends a command string to the RF device.
        This function is fully generic; device syntax is abstracted out.
        """
        if not self.connected or not self.serial_handle:
            return
        try:
            self.serial_handle.write(f"{cmd}\r\n".encode())
        except Exception as e:
            print(f"[ERROR] TX failed: {e}")

    def read_response(self):
        """
        Reads a response from the RF device, if available.
        Blocking read is avoided using small timeout windows.
        """
        if not self.connected:
            return None
        try:
            if self.serial_handle.in_waiting:
                data = self.serial_handle.readline().decode(errors="ignore").strip()
                if data:
                    self.rx_queue.put(data)
                    return data
        except Exception as e:
            print(f"[ERROR] RX failed: {e}")
        return None

    # ---------------------------------------------------------------
    # Polling Thread
    # ---------------------------------------------------------------

    def start_polling(self, interval: float = 1.0):
        """Begins periodic polling of device status."""
        if not self.connected:
            print("[WARN] Cannot start polling: no active connection.")
            return
        self.polling_active = True
        threading.Thread(target=self._polling_loop, args=(interval,), daemon=True).start()

    def _polling_loop(self, interval):
        """Continuously polls the device for updated information."""
        while self.polling_active and not self._stop_event.is_set():
            self.send_command("STATUS?")
            response = self.read_response()
            if response:
                self._process_status(response)
            time.sleep(interval)

    def _process_status(self, response: str):
        """Parses generic status messages (placeholder for real device logic)."""
        # Example: STATUS:LOCKED,FREQ=2400.0,POWER=10
        if "LOCKED" in response:
            print(f"[INFO] Device Locked | Raw: {response}")
        else:
            print(f"[INFO] Status: {response}")

    # ---------------------------------------------------------------
    # Sweep Control
    # ---------------------------------------------------------------

    def run_sweep(self, start_freq, stop_freq, step_hz=1e6, dwell_ms=200):
        """Performs a simulated or abstracted frequency sweep."""
        if not self.connected:
            print("[WARN] Cannot start sweep: not connected.")
            return

        self._sweep_active = True
        self._stop_event.clear()
        threading.Thread(
            target=self._sweep_loop, args=(start_freq, stop_freq, step_hz, dwell_ms), daemon=True
        ).start()

    def _sweep_loop(self, start_freq, stop_freq, step_hz, dwell_ms):
        """Internal sweep loop."""
        print("[INFO] Sweep started.")
        current = start_freq
        while self._sweep_active and not self._stop_event.is_set():
            self.send_command(f"SETFREQ {current}")
            print(f"[DEBUG] Sweeping → {current:.2f} Hz")
            current += step_hz
            if current >= stop_freq:
                print("[INFO] Sweep complete.")
                break
            time.sleep(dwell_ms / 1000.0)
        self._sweep_active = False

    def stop_sweep(self):
        """Stops the active sweep."""
        if self._sweep_active:
            self._sweep_active = False
            self._stop_event.set()
            print("[INFO] Sweep stopped.")

    # ---------------------------------------------------------------
    # Utility
    # ---------------------------------------------------------------

    def mark_sweep_start(self):
        """Lifecycle marker placeholder."""
        print("[MARK] Sweep start.")

    def mark_sweep_end(self):
        """Lifecycle marker placeholder."""
        print("[MARK] Sweep end.")
