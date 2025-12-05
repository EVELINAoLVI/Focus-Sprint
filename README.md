# Focus-Sprint
A graphical application that uses Linux system libraries and retrieves/stores data from the system.

# SysGlimpse

SysGlimpse is a native Linux desktop application built during a Lux Vitae Focus Sprint. It visualizes system telemetry and demonstrates compliance with Linux storage standards.

**Built with:** Python, GTK4, and Libadwaita.

## Features
*   **System Retrieval:** Parses `/etc/os-release` for distribution details and `/proc/meminfo` for real-time memory usage.
*   **XDG Compliance:** Follows the XDG Base Directory specification to safely store application data in `~/.local/share/sysglimpse/`.
*   **Modern UI:** Utilizes Libadwaita for a responsive, GNOME-native look.

## How to Run
1. Install dependencies (Ubuntu/Debian):
   ```bash
   sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 gir1.2-adw-1
