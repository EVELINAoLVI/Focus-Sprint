import sys
import os
import json
import gi
from pathlib import Path

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib

class SysGlimpseWindow(Adw.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title="SysGlimpse")
        self.set_default_size(600, 600)

        # --- UI SETUP ---
        # main layout
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        
        # header bar
        header = Adw.HeaderBar()
        box.append(header)

        # scrollable content area
        scroll = Gtk.ScrolledWindow()
        scroll.set_vexpand(True)
        
        # clamp layout
        clamp = Adw.Clamp()
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        content_box.set_margin_top(24)
        content_box.set_margin_bottom(24)
        content_box.set_margin_start(12)
        content_box.set_margin_end(12)
        
        clamp.set_child(content_box)
        scroll.set_child(clamp)
        box.append(scroll)

        # layout (icon left | text right) 
        header_container = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=24)
        header_container.set_halign(Gtk.Align.CENTER) # Center the whole group
        header_container.set_margin_bottom(12)

        # 1. the icon (left)
        self.icon_img = Gtk.Image.new_from_icon_name("computer-symbolic")
        self.icon_img.set_pixel_size(96) # make it big
        header_container.append(self.icon_img)

        # 2. the text (right) - vertical stack for title + description
        text_stack = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        text_stack.set_valign(Gtk.Align.CENTER) # Center vertically against icon

        self.title_label = Gtk.Label(label="System Ready")
        self.title_label.add_css_class("title-1") # Make font large
        self.title_label.set_xalign(0) # Align text to the left
        text_stack.append(self.title_label)

        self.desc_label = Gtk.Label(label="Gathering system telemetry...")
        self.desc_label.add_css_class("body")
        self.desc_label.set_xalign(0) # Align text to the left
        text_stack.append(self.desc_label)

        header_container.append(text_stack)
        content_box.append(header_container)
        # --------------------------------------------------

        # 2. preferences group
        info_group = Adw.PreferencesGroup()
        info_group.set_title("System Information")

        self.row_hostname = Adw.ActionRow()
        self.row_hostname.set_title("Hostname")
        self.row_hostname.set_subtitle("Loading...")
        self.row_hostname.set_icon_name("network-server-symbolic")
        info_group.add(self.row_hostname)

        self.row_os = Adw.ActionRow()
        self.row_os.set_title("Operating System")
        self.row_os.set_subtitle("Loading...")
        self.row_os.set_icon_name("preferences-desktop-symbolic")
        info_group.add(self.row_os)

        self.row_ram = Adw.ActionRow()
        self.row_ram.set_title("Memory Usage")
        self.row_ram.set_subtitle("Calculating...")
        self.row_ram.set_icon_name("drive-harddisk-solidstate-symbolic")
        info_group.add(self.row_ram)

        content_box.append(info_group)

        # 3. action button
        save_btn = Gtk.Button(label="Save Snapshot")
        save_btn.add_css_class("pill")
        save_btn.add_css_class("suggested-action")
        save_btn.connect("clicked", self.save_snapshot)
        content_box.append(save_btn)

        self.toast_overlay = Adw.ToastOverlay()
        self.toast_overlay.set_child(box)
        self.set_content(self.toast_overlay)

        # load data
        self.load_system_data()

    def load_system_data(self):
        import socket
        hostname = socket.gethostname()
        self.row_hostname.set_subtitle(hostname)
        
        # update the new header labels
        self.title_label.set_label(hostname)

        os_name = "Unknown Linux"
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        os_name = line.split("=")[1].strip().strip('"')
                        break
        except FileNotFoundError:
            pass
        self.row_os.set_subtitle(os_name)
        
        # update the description label
        self.desc_label.set_label(f"Running {os_name}")

        try:
            mem_total = 0
            mem_avail = 0
            with open("/proc/meminfo") as f:
                for line in f:
                    if "MemTotal" in line:
                        mem_total = int(line.split()[1])
                    elif "MemAvailable" in line:
                        mem_avail = int(line.split()[1])
            
            if mem_total > 0:
                used_gb = (mem_total - mem_avail) / 1024 / 1024
                total_gb = mem_total / 1024 / 1024
                self.row_ram.set_subtitle(f"{used_gb:.2f} GB / {total_gb:.2f} GB")
        except Exception as e:
            self.row_ram.set_subtitle("Error reading memory")

    def save_snapshot(self, button):
        xdg_data = os.environ.get("XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share"))
        app_dir = os.path.join(xdg_data, "sysglimpse")
        
        Path(app_dir).mkdir(parents=True, exist_ok=True)
        
        data = {
            "hostname": self.row_hostname.get_subtitle(),
            "os": self.row_os.get_subtitle(),
            "ram": self.row_ram.get_subtitle()
        }

        file_path = os.path.join(app_dir, "snapshot.json")
        with open(file_path, "w") as f:
            json.dump(data, f, indent=4)
        
        toast = Adw.Toast.new(f"Saved to {file_path}")
        self.toast_overlay.add_toast(toast)

class SysGlimpseApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id="com.luxvitae.sysglimpse",
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = SysGlimpseWindow(self)
        win.present()

if __name__ == "__main__":
    app = SysGlimpseApp()
    app.run(sys.argv)