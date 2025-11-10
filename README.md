# **Smart_PLL_Interface**
### Real-Time Control and Monitoring GUI

---
**NDA-compliant educational release** of the framework designed for Z-Communications’ line of **Smart SSG PLL products**, providing a cross-compatible, Python-based GUI for serial control and monitoring.

---

### Overview
This project demonstrates the **core architecture** of a real-time GUI used to interface with MCU-controlled PLL synthesizers.  
The GUI layer runs asynchronously, handling command queues, serial polling, and sweep control while the MCU manages timing and RF loop operations.

This framework was developed with reliability and timing practices aligned with high-performance RF systems used in aerospace and advanced communication applications.

---

### Framework Highlights
- **Serial Communication:** auto-detect, safe connect/disconnect, non-blocking TX/RX  
- **Threaded Control Layer:** independent polling and sweep threads  
- **Synchronized Polling:** aligned with firmware timing; GUI never dictates pacing  
- **Sweep Engine:** range-based control with step/dwell parameters  
- **Crash-Safe:** graceful recovery from disconnects and timeouts  
- **Cross-Compatible:** supports multiple Smart PLL variants

---

### Structure
```text
Smart_PLL_Interface/
│
├── gui_main.py # GUI frontend – controls and display
├── rf_controller.py # Backend – serial I/O and sweep logic
├── README.md # Documentation
└── LICENSE # MIT (educational use)
```

---

### Purpose
Educational reference for engineers or students learning:
- GUI ↔ MCU synchronization
- Serial communication and threading
- Real-time embedded control abstractions

---

### Disclaimer
This release is a **sanitized derivative** for demonstration and educational use only.  
All proprietary firmware commands, hardware identifiers, and confidential data have been removed.
