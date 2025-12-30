"""Main entry point for Omniboard Launcher application."""
from gui import MongoApp


def main():
    """Launch the Omniboard application."""
    app = MongoApp()
    app.mainloop()


if __name__ == "__main__":
    main()
