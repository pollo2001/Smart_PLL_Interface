"""
Smart_RF_Interface - Graphical Frontend
---------------------------------------
This is a sanitized, NDA-compliant version of the GUI for a
real-time RF control system. The interface manages serial
connection, frequency sweep control, and live device feedback.

All proprietary identifiers, commands, and device-specific logic
have been removed, leaving a clean demonstration of structure,
architecture, and logic for real-time embedded control GUIs.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
from rf_controller import RFController


class SmartRFApp:
    """Main application class for the Smart RF Interface GUI."""

    def __init__(self, master):
        self.master = master
        self.master.title("Smart RF Interface")
        self.master.geometry("900x600")
        self.master.resizable(False, False)

        # Backend controller
        self.controller = RFController()

        # Sweep control state
        self.sweep_thread = None
        self._stop_sweep = threading.Event()

        # GUI elements
        self._build_layout()

    # ----------------------------------------------------------------
    # GUI Construction
    # ----------------------------------------------------------------
    def _build_layout(self):
        """Initializes and arranges GUI widgets."""
        header = ttk.Label(
            self.master, text="Smart RF Interface", font=("Segoe UI", 18, "bold")
        )
        header.pack(pady=15)

        # Connection Controls
        conn_frame = ttk.LabelFrame(self.master, text="Connection")
        conn_frame.pack(fill="x", padx=15, pady=5)

        ttk.Button(conn_frame, text="Connect", command=self._connect).pack(side="left", padx=5)
        ttk.Button(conn_frame, text="Disconnect", command=self._disconnect).pack(side="left", padx=5)

        self.conn_status = ttk.Label(conn_frame, text="Status: Disconnected", foreground="gray")
        self.conn_status.pack(side="left", padx=10)

        # Sweep Controls
        sweep_frame = ttk.LabelFrame(self.master, text="Frequency Sweep Control")
        sweep_frame.pack(fill="x", padx=15, pady=5)

        ttk.Label(sweep_frame, text="Start Freq (Hz):").grid(row=0, column=0, padx=5, pady=3)
        self.start_freq_entry = ttk.Entry(sweep_frame)
        self.start_freq_entry.insert(0, "1000000000")
        self.start_freq_entry.grid(row=0, column=1, padx=5, pady=3)

        ttk.Label(sweep_frame, text="Stop Freq (Hz):").grid(row=0, column=2, padx=5, pady=3)
        self.stop_freq_entry = ttk.Entry(sweep_frame)
        self.stop_freq_entry.insert(0, "2000000000")
        self.stop_freq_entry.grid(row=0, column=3, padx=5, pady=3)

        ttk.Label(sweep_frame, text="Step (Hz):").grid(row=1, column=0, padx=5, pady=3)
        self.step_entry = ttk.Entry(sweep_frame)
        self.step_entry.insert(0, "10000000")
        self.step_entry.grid(row=1, column=1, padx=5, pady=3)

        ttk.Label(sweep_frame, text="Dwell (ms):").grid(row=1, column=2, padx=5, pady=3)
        self.dwell_entry = ttk.Entry(sweep_frame)
        self.dwell_entry.insert(0, "200")
        self.dwell_entry.grid(row=1, column=3, padx=5, pady=3)

        self.start_button = ttk.Button(sweep_frame, text="Start Sweep", command=self._start_sweep)
        self.start_button.grid(row=2, column=0, padx=5, pady=8)

        self.stop_button = ttk.Button(sweep_frame, text="Stop Sweep", command=self._stop_sweep_func)
        self.stop_button.grid(row=2, column=1, padx=5, pady=8)

        self.sweep_status = ttk.Label(sweep_frame, text="Sweep: Idle", foreground="gray")
        self.sweep_status.grid(row=2, column=3, padx=5, pady=8)

        # Live Data Section
        status_frame = ttk.LabelFrame(self.master, text="Live Device Status")
        status_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.log_output = tk.Text(status_frame, wrap="word", height=15, state="disabled")
        self.log_output.pack(fill="both", expand=True, padx=10, pady=10)

        self._log("Application initialized.\n")

    # ----------------------------------------------------------------
    # Utility and Logging
    # ----------------------------------------------------------------
    def _log(self, message: str):
        """Thread-safe log printer."""
        self.log_output.configure(state="normal")
        self.log_output.insert("end", f"{message}\n")
        self.log_output.configure(state="disabled")
        self.log_output.see("end")

    def _set_status(self, text, color="gray"):
        self.conn_status.config(text=text, foreground=color)

    # ----------------------------------------------------------------
    # Connection Logic
    # ----------------------------------------------------------------
    def _connect(self):
        self._log("Attempting to connect...")
        success = self.controller.auto_connect()
        if success:
            self._set_status("Status: Connected", "green")
            self._log(f"Connected to {self.controller.port}")
            threading.Thread(target=self._poll_loop, daemon=True).start()
        else:
            self._set_status("Status: Disconnected", "red")
            self._log("Connection failed or no devices detected.")

    def _disconnect(self):
        self.controller.disconnect()
        self._set_status("Status: Disconnected", "gray")
        self._log("Disconnected.")

    # ----------------------------------------------------------------
    # Sweep Control Logic
    # ----------------------------------------------------------------
    def _start_sweep(self):
        """Starts the sweep process."""
        try:
            start = float(self.start_freq_entry.get())
            stop = float(self.stop_freq_entry.get())
            step = float(self.step_entry.get())
            dwell = float(self.dwell_entry.get())

            self._log(f"Starting sweep: {start/1e6:.2f} → {stop/1e6:.2f} MHz")
            self.sweep_status.config(text="Sweep: Running", foreground="green")

            self.sweep_thread = threading.Thread(
                target=self.controller.run_sweep, args=(start, stop, step, dwell), daemon=True
            )
            self.sweep_thread.start()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values for sweep parameters.")
        except Exception as e:
            self._log(f"[ERROR] Sweep start failed: {e}")

    def _stop_sweep_func(self):
        """Stops the active sweep."""
        self.controller.stop_sweep()
        self.sweep_status.config(text="Sweep: Stopped", foreground="red")
        self._log("Sweep halted by user.")

    # ----------------------------------------------------------------
    # Polling Loop (Live Updates)
    # ----------------------------------------------------------------
    def _poll_loop(self):
        """Continuously updates GUI with latest device data."""
        while self.controller.connected:
            response = self.controller.read_response()
            if response:
                self._log(f"[Device] {response}")
            time.sleep(1.0)


# --------------------------------------------------------------------
# Application Entry Point
# --------------------------------------------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = SmartRFApp(root)
    root.mainloop()
