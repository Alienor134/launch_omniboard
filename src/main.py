"""Main entry point for Omniboard Launcher application."""
import os
import sys
import webbrowser
import threading
import time
from app import create_dash_app


def is_executable_mode():
    """Check if running as a PyInstaller executable."""
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def open_browser(url, delay=2):
    """Open browser after a short delay."""
    time.sleep(delay)
    webbrowser.open(url)


def main():
    """Launch the Omniboard application in appropriate mode."""
    app = create_dash_app()
    
    port = int(os.environ.get("PORT", 8060))
    
    if is_executable_mode():
        # Desktop executable mode: Auto-open browser
        print(f"Starting AltarViewer on http://localhost:{port}")
        print("Opening browser...")
        
        # Open browser in background thread
        threading.Thread(target=open_browser, args=(f"http://localhost:{port}",), daemon=True).start()
        
        # Run server
        app.run(debug=False, port=port, host="127.0.0.1")
    else:
        # Docker/development mode: Listen on all interfaces
        host = "0.0.0.0" if os.environ.get("DOCKER_MODE") else "127.0.0.1"
        debug = os.environ.get("DEBUG", "false").lower() == "true"
        
        print(f"Starting AltarViewer on http://localhost:{port}")
        app.run(debug=debug, port=port, host=host)


if __name__ == "__main__":
    main()
