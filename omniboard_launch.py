import os
import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
import subprocess
import sys
import socket

class MongoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MongoDB Database Selector")
        self.geometry("500x600")
        self.resizable(False, False)

        self.port_var = tk.StringVar(value="27017")
        self.db_list = []
        self.selected_db = tk.StringVar()

        # Connection type (only local)
        ttk.Label(self, text="Connect to local MongoDB:").pack(anchor="w", padx=10, pady=(10, 0))

        # Port entry for local
        self.port_frame = ttk.Frame(self)
        self.port_frame.pack(anchor="w", padx=10, pady=(5, 0))
        ttk.Label(self.port_frame, text="Port:").pack(side="left")
        self.port_entry = ttk.Entry(self.port_frame, textvariable=self.port_var, width=8)
        self.port_entry.pack(side="left")

        # Connect button
        self.connect_btn = ttk.Button(self, text="Connect", command=self.connect)
        self.connect_btn.pack(pady=10)

        # Listbox for databases
        self.db_listbox = tk.Listbox(self, height=15, exportselection=False)
        self.db_listbox.pack(fill="x", padx=10, pady=(5, 0))
        self.db_listbox.bind("<<ListboxSelect>>", self.on_db_select)

        # Selected db label
        self.selected_label = ttk.Label(self, text="")
        self.selected_label.pack(pady=10)

        # Launch Omniboard button (always visible, but disabled initially)
        self.launch_btn = ttk.Button(self, text="Launch Omniboard", command=self.launch_omniboard, state=tk.DISABLED)
        self.launch_btn.pack(pady=10)

        # Button to clear all Omniboard Docker containers
        self.clear_docker_btn = ttk.Button(self, text="Clear Omniboard Docker Containers", command=self.clear_omniboard_docker)
        self.clear_docker_btn.pack(pady=5)

        # Info label for Omniboard port (clickable link, multiline)
        self.omniboard_info_label = tk.Label(self, text="", fg="blue", cursor="hand2", justify="left", anchor="w")
        self.omniboard_info_label.pack(fill="x", padx=10, pady=5)
        self.omniboard_info_label.bind("<Button-1>", self.open_omniboard_link)
        self.omniboard_url = None
        self.omniboard_info_lines = []

    def get_mongo_uri(self):
        port = self.port_var.get() or "27017"
        return f"mongodb://localhost:{port}/"

    def connect(self):
        self.db_listbox.delete(0, tk.END)
        self.selected_label.config(text="")
        uri = self.get_mongo_uri()
        if not uri:
            messagebox.showerror("Error", "Missing port for local MongoDB.")
            return
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            dbs = client.list_database_names()
            self.db_list = dbs
            for db in dbs:
                self.db_listbox.insert(tk.END, db)
            if not dbs:
                self.db_listbox.insert(tk.END, "<No databases found>")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def on_db_select(self, event):
        sel = self.db_listbox.curselection()
        if sel:
            db_name = self.db_listbox.get(sel[0])
            self.selected_label.config(text=f"Selected database: {db_name}")
            self.selected_db.set(db_name)
            self.launch_btn.config(state=tk.NORMAL)
        else:
            self.selected_label.config(text="")
            self.selected_db.set("")
            self.launch_btn.config(state=tk.DISABLED)

    def find_free_port(self, start_port=9005, max_tries=20):
        port = int(start_port)
        for _ in range(max_tries):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("", port))
                except OSError:
                    port += 1
                    continue
            try:
                result = subprocess.run(
                    ["docker", "ps", "--filter", f"publish={port}", "--format", "{{.ID}}"],
                    capture_output=True, text=True
                )
                if result.stdout.strip() == "":
                    return str(port)
            except Exception:
                return str(port)
            port += 1
        raise RuntimeError("No free port found for Omniboard.")

    def clear_omniboard_docker(self):
        try:
            # Remove all containers with name starting with 'omniboard_'
            result = subprocess.run(
                'docker ps -a --filter "name=omniboard_" --format "{{.ID}}"',
                shell=True, capture_output=True, text=True
            )
            container_ids = result.stdout.strip().splitlines()
            if not container_ids:
                messagebox.showinfo("Docker", "No Omniboard containers to remove.")
                # Also clear the Omniboard info label and lines
                self.omniboard_info_lines.clear()
                self.omniboard_info_label.config(text="")
                return
            for cid in container_ids:
                subprocess.run(f"docker rm -f {cid}", shell=True)
            # Clear the Omniboard info label and lines
            self.omniboard_info_lines.clear()
            self.omniboard_info_label.config(text="")
            messagebox.showinfo("Docker", "All Omniboard containers removed.")
        except Exception as e:
            messagebox.showerror("Docker Error", str(e))

    def launch_omniboard(self):
        db_name = self.selected_db.get()
        if not db_name:
            messagebox.showerror("Error", "No database selected.")
            return

        try:
            host_port = self.find_free_port(9005)
        except RuntimeError as e:
            messagebox.showerror("Port Error", str(e))
            return

        port = self.port_var.get() or "27017"
        if sys.platform.startswith("win") or sys.platform == "darwin":
            mongo_host = "host.docker.internal"
        else:
            mongo_host = "localhost"
        mongo_arg = f"{mongo_host}:{port}:{db_name}"

        import uuid
        container_name = f"omniboard_{uuid.uuid4().hex[:8]}"

        docker_cmd = [
            "docker", "run", "-it", "--rm", "-p", f"{host_port}:9000", "--name", container_name,
            "vivekratnavel/omniboard", "-m", mongo_arg
        ]

        try:
            subprocess.Popen(docker_cmd)
            url = f"http://localhost:{host_port}"
            self.omniboard_url = url
            line = f"Omniboard for '{db_name}': Click here to open: {url}"
            self.omniboard_info_lines.append(line)
            self.omniboard_info_label.config(text="\n".join(self.omniboard_info_lines))
        except Exception as e:
            messagebox.showerror("Launch Error", str(e))

    def open_omniboard_link(self, event):
        # Open the last launched Omniboard link
        if self.omniboard_url:
            import webbrowser
            webbrowser.open(self.omniboard_url)

"""
To turn this script into an executable:

1. Install PyInstaller (recommended):
   pip install pyinstaller

2. From a terminal in this script's directory, run:
   pyinstaller --onefile --windowed omniboard_launch.py

   - The --windowed flag prevents a console window from appearing.
   - The --onefile flag bundles everything into a single executable.

3. The executable will be in the 'dist' folder.

Notes:
- PyInstaller will bundle pymongo and other imported modules into the executable automatically.
- You do NOT need to install pymongo separately on the target machine.
- However, you DO need Docker installed and available on the target machine.
- If you use non-standard modules, PyInstaller usually detects them, but you may need to specify hidden imports.
- For icons, add: --icon=youricon.ico

For more options, see: https://pyinstaller.org/
"""

if __name__ == "__main__":
    app = MongoApp()
    app.mainloop()
