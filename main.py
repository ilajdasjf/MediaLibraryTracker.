#!/usr/bin/env python3
"""
Main entry point for the Media Catalog application.
"""
import tkinter as tk
from gui import MediaCatalogGUI

def main():
    """Run the media catalog application."""
    try:
        root = tk.Tk()
        app = MediaCatalogGUI(root)
        root.mainloop()
    except KeyboardInterrupt:
        print("\nApplication closed by user")
    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()
