import customtkinter as ctk
from tkinter import messagebox
from pymongo import MongoClient
import subprocess
import sys
import socket
import hashlib
import webbrowser
import uuid
from urllib.parse import urlparse

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Dark", "Light"

class MongoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MongoDB Database Selector")
        self.geometry("550x700")
        self.resizable(False, False)
        
        # Hide window initially to allow background loading
        self.withdraw()

        self.port_var = ctk.StringVar(value="27017")
        self.mongo_url_var = ctk.StringVar(value="")
        self.connection_mode = ctk.StringVar(value="Port")
        self.db_list = []
        self.selected_db = ctk.StringVar()

        # Configure grid weight
        self.grid_columnconfigure(0, weight=1)

        # Title Label
        title_label = ctk.CTkLabel(
            self, 
            text="MongoDB & Omniboard Launcher",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")

        # Connection Frame
        self.connection_frame = ctk.CTkFrame(self)
        self.connection_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        self.connection_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self.connection_frame, 
            text="Connect to MongoDB",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=10, pady=(5, 2), sticky="w")

        # Connection mode selector
        self.mode_selector = ctk.CTkSegmentedButton(
            self.connection_frame,
            values=["Port", "Full URL"],
            variable=self.connection_mode,
            command=self.on_connection_mode_change
        )
        self.mode_selector.grid(row=1, column=0, columnspan=2, padx=10, pady=2, sticky="ew")

        # Port entry
        self.port_label = ctk.CTkLabel(self.connection_frame, text="Port:")
        self.port_label.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
        self.port_entry = ctk.CTkEntry(
            self.connection_frame, 
            textvariable=self.port_var,
            width=100,
            placeholder_text="27017"
        )
        self.port_entry.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="w")

        # MongoDB URL entry (initially hidden)
        self.url_label = ctk.CTkLabel(self.connection_frame, text="MongoDB URL:")
        self.url_entry = ctk.CTkEntry(
            self.connection_frame,
            textvariable=self.mongo_url_var,
            placeholder_text="mongodb://localhost:27017/"
        )
        self.url_label.grid_remove()
        self.url_entry.grid_remove()

        # Connect button
        self.connect_btn = ctk.CTkButton(
            self.connection_frame,
            text="Connect to MongoDB",
            command=self.connect,
            height=28,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.connect_btn.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

        # Database Selection Frame
        self.db_frame = ctk.CTkFrame(self)
        self.db_frame.grid(row=2, column=0, padx=20, pady=5, sticky="nsew")
        self.db_frame.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            self.db_frame,
            text="Available Databases",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(5, 2), sticky="w")

        # Scrollable frame for databases
        self.db_scrollable_frame = ctk.CTkScrollableFrame(self.db_frame, height=300, fg_color=("gray95", "gray20"))
        self.db_scrollable_frame.grid(row=1, column=0, padx=10, pady=2, sticky="nsew")
        self.db_frame.grid_rowconfigure(1, weight=1)
        
        self.db_labels = []
        self.selected_db_label = None

        # Selected database label
        self.selected_label = ctk.CTkLabel(
            self.db_frame,
            text="No database selected",
            font=ctk.CTkFont(size=12),
            text_color="gray70"
        )
        self.selected_label.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Omniboard Control Frame
        self.omniboard_frame = ctk.CTkFrame(self)
        self.omniboard_frame.grid(row=3, column=0, padx=20, pady=5, sticky="ew")
        self.omniboard_frame.grid_columnconfigure(0, weight=1)

        # Launch Omniboard button
        self.launch_btn = ctk.CTkButton(
            self.omniboard_frame,
            text="Launch Omniboard",
            command=self.launch_omniboard,
            state="disabled",
            height=32,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#1f6aa5",
            hover_color="#144870"
        )
        self.launch_btn.grid(row=0, column=0, padx=10, pady=(5, 3), sticky="ew")

        # Clear Docker containers button
        self.clear_docker_btn = ctk.CTkButton(
            self.omniboard_frame,
            text="Clear All Omniboard Containers",
            command=self.clear_omniboard_docker,
            height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#8B0000",
            hover_color="#660000"
        )
        self.clear_docker_btn.grid(row=1, column=0, padx=10, pady=3, sticky="ew")

        # Omniboard info textbox (for clickable links)
        self.omniboard_info_text = ctk.CTkTextbox(
            self.omniboard_frame,
            height=60,
            wrap="word",
            font=ctk.CTkFont(size=11)
        )
        self.omniboard_info_text.grid(row=2, column=0, padx=10, pady=(3, 5), sticky="ew")
        self.omniboard_info_text.configure(state="disabled")
        
        # Configure link tag for blue, underlined, clickable text
        self.omniboard_info_text.tag_config("link", foreground="#1f6aa5", underline=True)
        self.omniboard_info_text.tag_bind("link", "<Button-1>", self.on_link_click)
        self.omniboard_info_text.tag_bind("link", "<Enter>", lambda e: self.omniboard_info_text.configure(cursor="hand2"))
        self.omniboard_info_text.tag_bind("link", "<Leave>", lambda e: self.omniboard_info_text.configure(cursor=""))
        
        # Show window after 2 second delay to allow background loading
        self.after(2000, self.deiconify)

    def on_connection_mode_change(self, value):
        """Toggle between Port and Full URL input modes."""
        if value == "Port":
            # Show port entry, hide URL entry
            self.port_label.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
            self.port_entry.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="w")
            self.url_label.grid_remove()
            self.url_entry.grid_remove()
        else:  # Full URL
            # Hide port entry, show URL entry
            self.port_label.grid_remove()
            self.port_entry.grid_remove()
            self.url_label.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
            self.url_entry.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="ew")

    def get_mongo_uri(self):
        """Get MongoDB connection URI based on selected mode."""
        if self.connection_mode.get() == "Port":
            port = self.port_var.get() or "27017"
            return f"mongodb://localhost:{port}/"
        else:  # Full URL
            url = self.mongo_url_var.get().strip()
            if not url:
                return None
            # Ensure it starts with mongodb://
            if not url.startswith("mongodb://") and not url.startswith("mongodb+srv://"):
                url = "mongodb://" + url
            return url

    def parse_mongo_url(self, url):
        """Parse MongoDB URL to extract host, port, and database for Omniboard.
        Returns tuple: (host, port, database)
        """
        parsed = urlparse(url)
        host = parsed.hostname or "localhost"
        port = parsed.port or 27017
        database = parsed.path.strip("/") if parsed.path else None
        return host, port, database

    def connect(self):
        # Clear previous database labels
        for label in self.db_labels:
            label.destroy()
        self.db_labels.clear()
        self.selected_db_label = None
        
        self.selected_label.configure(text="Connecting...")
        uri = self.get_mongo_uri()
        if not uri:
            messagebox.showerror("Error", "Please provide a valid MongoDB connection (port or URL).")
            self.selected_label.configure(text="Connection failed")
            return
        
        try:
            client = MongoClient(uri, serverSelectionTimeoutMS=3000)
            dbs = client.list_database_names()
            self.db_list = dbs
            
            if not dbs:
                self.selected_label.configure(text="No databases found")
                no_db_label = ctk.CTkLabel(
                    self.db_scrollable_frame,
                    text="No databases found",
                    text_color="gray60"
                )
                no_db_label.pack(pady=10)
                self.db_labels.append(no_db_label)
            else:
                for db in dbs:
                    label = ctk.CTkLabel(
                        self.db_scrollable_frame,
                        text=db,
                        height=22,
                        font=ctk.CTkFont(size=13),
                        cursor="hand2",
                        anchor="w",
                        padx=10,
                        fg_color="transparent"
                    )
                    label.pack(pady=0, padx=5, fill="x")
                    label.bind("<Button-1>", lambda e, d=db: self.select_database(d))
                    label.bind("<Enter>", lambda e, l=label: l.configure(fg_color=("gray85", "gray30")))
                    label.bind("<Leave>", lambda e, l=label: l.configure(fg_color="transparent") if l != self.selected_db_label else None)
                    self.db_labels.append(label)
                
                self.selected_label.configure(text="Please select a database")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.selected_label.configure(text="Connection failed")

    def select_database(self, db_name):
        self.selected_db.set(db_name)
        self.selected_label.configure(
            text=f"Selected: {db_name}",
            text_color=("#1f6aa5", "#5fb4ff")  # Different colors for light/dark mode
        )
        self.launch_btn.configure(state="normal")
        
        # Update label appearance to show selection
        for label in self.db_labels:
            if isinstance(label, ctk.CTkLabel) and label.cget("text") == db_name:
                label.configure(fg_color=("#1f6aa5", "#1f6aa5"), text_color="white")
                self.selected_db_label = label
            elif isinstance(label, ctk.CTkLabel) and label.cget("text") != "No databases found":
                label.configure(fg_color="transparent", text_color=("black", "white"))

    def port_for_db(self, db_name, base=20000, span=10000):
        """Generate a deterministic port number based on database name."""
        h = int(hashlib.sha256(db_name.encode()).hexdigest(), 16)
        return base + (h % span)

    def find_available_port(self, start_port):
        """Find an available port starting from the given port."""
        port = start_port
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("", port))
                    # Also check if Docker is using this port
                    try:
                        result = subprocess.run(
                            ["docker", "ps", "--filter", f"publish={port}", "--format", "{{.ID}}"],
                            capture_output=True, text=True
                        )
                        if result.stdout.strip() == "":
                            return port
                    except Exception:
                        return port
                except OSError:
                    port += 1

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
            else:
                for cid in container_ids:
                    subprocess.run(f"docker rm -f {cid}", shell=True)
                messagebox.showinfo("Docker", "All Omniboard containers removed.")
            
            # Clear the info textbox
            self.omniboard_info_text.configure(state="normal")
            self.omniboard_info_text.delete("1.0", "end")
            self.omniboard_info_text.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Docker Error", str(e))

    def launch_omniboard(self):
        db_name = self.selected_db.get()
        if not db_name:
            messagebox.showerror("Error", "No database selected.")
            return

        # Get deterministic port based on database name
        preferred_port = self.port_for_db(db_name)
        host_port = self.find_available_port(preferred_port)

        # Determine MongoDB connection details based on mode
        if self.connection_mode.get() == "Port":
            port = self.port_var.get() or "27017"
            mongo_host = "localhost"
        else:  # Full URL mode
            uri = self.get_mongo_uri()
            mongo_host, port, _ = self.parse_mongo_url(uri)
        
        # Adjust host for Docker
        if sys.platform.startswith("win") or sys.platform == "darwin":
            if mongo_host in ["localhost", "127.0.0.1"]:
                mongo_host = "host.docker.internal"
        
        mongo_arg = f"{mongo_host}:{port}:{db_name}"
        container_name = f"omniboard_{uuid.uuid4().hex[:8]}"
        docker_cmd = [
            "docker", "run", "-it", "--rm", "-p", f"{host_port}:9000", "--name", container_name,
            "vivekratnavel/omniboard", "-m", mongo_arg
        ]

        try:
            subprocess.Popen(docker_cmd)
            url = f"http://localhost:{host_port}"
            
            # Update textbox with clickable links
            self.omniboard_info_text.configure(state="normal")
            
            # Insert text with clickable URL
            text_before = f"Omniboard for '{db_name}': "
            self.omniboard_info_text.insert("end", text_before)
            
            # Insert URL as a clickable link
            url_start = self.omniboard_info_text.index("end-1c")
            self.omniboard_info_text.insert("end", url)
            url_end = self.omniboard_info_text.index("end-1c")
            
            # Apply both the visual 'link' tag and a unique URL tag
            self.omniboard_info_text.tag_add("link", url_start, url_end)
            self.omniboard_info_text.tag_add(f"url_{url}", url_start, url_end)
            
            self.omniboard_info_text.insert("end", "\n")
            self.omniboard_info_text.configure(state="disabled")
            
            # Open in browser after 2 second delay to allow Omniboard to start
            self.after(2000, lambda: webbrowser.open(url))
        except Exception as e:
            messagebox.showerror("Launch Error", str(e))

    def on_link_click(self, event):
        """Handle clicks on hyperlinks in the textbox."""
        try:
            # Get the index of the click
            index = self.omniboard_info_text.index(f"@{event.x},{event.y}")
            # Get all tags at this position
            tags = self.omniboard_info_text.tag_names(index)
            
            # Find the URL tag (starts with 'url_')
            for tag in tags:
                if tag.startswith('url_'):
                    url = tag[4:]  # Remove 'url_' prefix
                    webbrowser.open(url)
                    break
        except Exception:
            pass


if __name__ == "__main__":
    app = MongoApp()
    app.mainloop()


"""
To turn this script into an executable:

1. Install required packages:
   pip install customtkinter pymongo pyinstaller

2. From a terminal in this script's directory, run:
   pyinstaller --onefile --windowed omniboard_launch_ctk.py

   - The --windowed flag prevents a console window from appearing.
   - The --onefile flag bundles everything into a single executable.

3. The executable will be in the 'dist' folder.

Notes:
- PyInstaller will bundle customtkinter, pymongo and other imported modules automatically.
- You do NOT need to install these packages separately on the target machine.
- However, you DO need Docker installed and available on the target machine.
- CustomTkinter provides a modern, dark-mode UI with smooth animations.
- The appearance can be changed between "System", "Dark", and "Light" modes.
"""
