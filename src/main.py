"""Main entry point for Omniboard Launcher application."""
# Support both package execution (python -m src.main) and direct script runs (python src/main.py)
try:
    from .gui import MongoApp
except ImportError:
    from gui import MongoApp


def main():
    """Launch the Omniboard application."""
    app = MongoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
