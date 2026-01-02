"""Main application GUI using CustomTkinter."""
import customtkinter as ctk
from tkinter import messagebox
import webbrowser

from mongodb import MongoDBClient
from omniboard import OmniboardManager

# Set appearance mode and color theme
ctk.set_appearance_mode("dark")


class MongoApp(ctk.CTk):
    """Main application window for MongoDB Database Selector and Omniboard Launcher."""
    
    def __init__(self):
        """Initialize the main application window."""
        super().__init__()
        self.title("MongoDB Database Selector")
        self.geometry("550x700")
        self.resizable(False, False)
        
        # Hide window initially to allow background loading
        self.withdraw()

        # Initialize backend managers
        self.mongo_client = MongoDBClient()
        self.omniboard_manager = OmniboardManager()

        # UI state variables
        self.port_var = ctk.StringVar(value="27017")
        self.mongo_url_var = ctk.StringVar(value="mongodb://localhost:27017/")
        self.connection_mode = ctk.StringVar(value="Port")
        self.db_list = []
        self.selected_db = ctk.StringVar()

        # Configure grid weight
        self.grid_columnconfigure(0, weight=1)

        # Initialize UI components
        self._create_title()
        self._create_connection_frame()
        self._create_database_frame()
        self._create_omniboard_frame()
        
        # Show window after 2 second delay
        self.after(2000, self.deiconify)

    def _create_title(self):
        """Create the title label."""
        title_label = ctk.CTkLabel(
            self, 
            text="MongoDB & Omniboard Launcher",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, padx=20, pady=(10, 5), sticky="ew")

    def _create_connection_frame(self):
        """Create the connection configuration frame."""
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
            placeholder_text="mongodb://localhost:27017/",
            width=300
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

    def _create_database_frame(self):
        """Create the database selection frame."""
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
        self.db_scrollable_frame = ctk.CTkScrollableFrame(
            self.db_frame, 
            height=300, 
            fg_color=("gray95", "gray20")
        )
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

    def _create_omniboard_frame(self):
        """Create the Omniboard control frame."""
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

        # Label for Omniboard URLs
        ctk.CTkLabel(
            self.omniboard_frame,
            text="Omniboard URLs:",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w"
        ).grid(row=2, column=0, padx=10, pady=(5, 0), sticky="w")

        # Omniboard info textbox (for clickable links)
        self.omniboard_info_text = ctk.CTkTextbox(
            self.omniboard_frame,
            height=80,
            wrap="word",
            font=ctk.CTkFont(size=11)
        )
        self.omniboard_info_text.grid(row=3, column=0, padx=10, pady=(2, 5), sticky="ew")
        self.omniboard_info_text.configure(state="disabled")
        
        # Configure link tag for blue, underlined, clickable text
        self.omniboard_info_text.tag_config("link", foreground="#1f6aa5", underline=True)
        self.omniboard_info_text.tag_bind("link", "<Button-1>", self.on_link_click)
        self.omniboard_info_text.tag_bind("link", "<Enter>", 
                                          lambda e: self.omniboard_info_text.configure(cursor="hand2"))
        self.omniboard_info_text.tag_bind("link", "<Leave>", 
                                          lambda e: self.omniboard_info_text.configure(cursor=""))

    def on_connection_mode_change(self, value):
        """Toggle between Port and Full URL input modes."""
        if value == "Port":
            self.port_label.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
            self.port_entry.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="w")
            self.url_label.grid_remove()
            self.url_entry.grid_remove()
        else:  # Full URL
            self.port_label.grid_remove()
            self.port_entry.grid_remove()
            self.url_label.grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
            self.url_entry.grid(row=2, column=1, padx=(5, 10), pady=5, sticky="ew")

    def connect(self):
        """Connect to MongoDB and list available databases."""
        # Clear previous database labels
        for label in self.db_labels:
            label.destroy()
        self.db_labels.clear()
        self.selected_db_label = None
        
        self.selected_label.configure(text="Connecting...")
        
        try:
            # Connect based on mode
            if self.connection_mode.get() == "Port":
                port = self.port_var.get() or "27017"
                dbs = self.mongo_client.connect_by_port(port)
            else:
                url = self.mongo_url_var.get().strip()
                if not url:
                    messagebox.showerror("Error", "Please provide a valid MongoDB URL.")
                    self.selected_label.configure(text="Connection failed")
                    return
                dbs = self.mongo_client.connect_by_url(url)
            
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
                    label.bind("<Leave>", lambda e, l=label: l.configure(fg_color="transparent") 
                              if l != self.selected_db_label else None)
                    self.db_labels.append(label)
                
                self.selected_label.configure(text="Please select a database")
        except Exception as e:
            error_msg = str(e)
            
            # Provide friendlier error messages
            if "ServerSelectionTimeoutError" in error_msg or "timed out" in error_msg.lower():
                friendly_msg = (
                    "Cannot connect to MongoDB server.\n\n"
                    "Please ensure:\n"
                    "• MongoDB is running on the specified port\n"
                    "• The port number is correct\n"
                    "• Your firewall allows the connection"
                )
            elif "connection refused" in error_msg.lower():
                friendly_msg = (
                    "Connection refused by MongoDB server.\n\n"
                    "MongoDB may not be running on this port.\n"
                    "Please start MongoDB or verify the port number."
                )
            elif "authentication failed" in error_msg.lower():
                friendly_msg = (
                    "MongoDB authentication failed.\n\n"
                    "Please check your username and password in the connection URL."
                )
            else:
                friendly_msg = f"Connection Error:\n\n{error_msg}"
            
            messagebox.showerror("MongoDB Connection Failed", friendly_msg)
            self.selected_label.configure(text="Connection failed")

    def select_database(self, db_name):
        """Select a database and enable the launch button."""
        self.selected_db.set(db_name)
        self.selected_label.configure(
            text=f"Selected: {db_name}",
            text_color=("#1f6aa5", "#5fb4ff")
        )
        self.launch_btn.configure(state="normal")
        
        # Update label appearance to show selection
        for label in self.db_labels:
            if isinstance(label, ctk.CTkLabel) and label.cget("text") == db_name:
                label.configure(fg_color=("#1f6aa5", "#1f6aa5"), text_color="white")
                self.selected_db_label = label
            elif isinstance(label, ctk.CTkLabel) and label.cget("text") != "No databases found":
                label.configure(fg_color="transparent", text_color=("black", "white"))

    def launch_omniboard(self):
        """Launch Omniboard in a Docker container for the selected database."""
        db_name = self.selected_db.get()
        if not db_name:
            messagebox.showerror("Error", "No database selected.")
            return

        try:
            # Get MongoDB connection details
            mongo_host, mongo_port, _ = self.mongo_client.parse_connection_url()
            
            # Launch Omniboard
            container_name, host_port = self.omniboard_manager.launch(
                db_name=db_name,
                mongo_host=mongo_host,
                mongo_port=mongo_port
            )
            
            url = f"http://localhost:{host_port}"
            
            # Update textbox with clickable link
            self.omniboard_info_text.configure(state="normal")
            text_before = f"Omniboard for '{db_name}': "
            self.omniboard_info_text.insert("end", text_before)
            
            # Insert URL as a clickable link
            url_start = self.omniboard_info_text.index("end-1c")
            self.omniboard_info_text.insert("end", url)
            url_end = self.omniboard_info_text.index("end-1c")
            
            # Apply tags
            self.omniboard_info_text.tag_add("link", url_start, url_end)
            self.omniboard_info_text.tag_add(f"url_{url}", url_start, url_end)
            
            self.omniboard_info_text.insert("end", "\n")
            self.omniboard_info_text.configure(state="disabled")
            
            # Open in browser after 4 second delay to allow Omniboard to fully start
            self.after(4000, lambda: webbrowser.open(url))
        except Exception as e:
            messagebox.showerror("Launch Error", str(e))

    def clear_omniboard_docker(self):
        """Remove all Omniboard Docker containers."""
        try:
            count = self.omniboard_manager.clear_all_containers()
            
            if count == 0:
                messagebox.showinfo("Docker", "No Omniboard containers to remove.")
            else:
                messagebox.showinfo("Docker", f"Removed {count} Omniboard container(s).")
            
            # Clear the info textbox
            self.omniboard_info_text.configure(state="normal")
            self.omniboard_info_text.delete("1.0", "end")
            self.omniboard_info_text.configure(state="disabled")
        except Exception as e:
            messagebox.showerror("Docker Error", str(e))

    def on_link_click(self, event):
        """Handle clicks on hyperlinks in the textbox."""
        try:
            index = self.omniboard_info_text.index(f"@{event.x},{event.y}")
            tags = self.omniboard_info_text.tag_names(index)
            
            for tag in tags:
                if tag.startswith('url_'):
                    url = tag[4:]
                    webbrowser.open(url)
                    break
        except Exception:
            pass
