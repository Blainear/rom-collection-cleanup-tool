#!/usr/bin/env python
"""
ROM Collection Cleanup Tool - GUI Version

A streamlined, user-friendly GUI tool for managing ROM collections
by removing duplicates based on region preferences while preserving
unique releases.
"""

import json
import logging
import shutil
import threading
import tkinter as tk
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Dict

from credential_manager import get_credential_manager
from rom_utils import get_base_name, get_region

# Import IGDB functionality from rom_cleanup.py
try:
    from rom_cleanup import query_igdb_game
except ImportError:
    query_igdb_game = None

try:
    import requests
except ImportError:
    requests = None
    print(
        "The 'requests' library is required for TheGamesDB features. "
        "Please install it to enable them."
    )

from tgdb_query import get_canonical_name, query_tgdb_game

# Default public API key for TheGamesDB - works out of the box for all users
DEFAULT_TGDB_API_KEY = "a353d6c0655d0d57a818a6f8a4417da239e752c060bcb52cb27793dc49285112"  # Default public API key

# Try to import pyperclip for clipboard functionality
try:
    import pyperclip

    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

# Global variables
GAME_CACHE = {}  # For caching game queries
CACHE_FILE = Path("rom_game_cache.json")  # Cache file path


def query_game_api(
    game_name,
    file_extension,
    api_choice,
    tgdb_api_key=None,
    igdb_client_id=None,
    igdb_access_token=None,
):
    """Unified function to query either TheGamesDB or IGDB based on user choice."""
    if api_choice == "thegamesdb" and tgdb_api_key:
        return query_tgdb_game(game_name, file_extension, tgdb_api_key)
    elif (
        api_choice == "igdb"
        and query_igdb_game
        and igdb_client_id
        and igdb_access_token
    ):
        # Set global variables in rom_cleanup module before calling
        import rom_cleanup

        rom_cleanup.IGDB_CLIENT_ID = igdb_client_id
        rom_cleanup.IGDB_ACCESS_TOKEN = igdb_access_token
        return query_igdb_game(game_name, file_extension)
    else:
        print(f"No valid API configuration for {api_choice}")
        return None


def get_unified_canonical_name(
    game_name,
    file_extension,
    api_choice,
    tgdb_api_key=None,
    igdb_client_id=None,
    igdb_access_token=None,
    logger=None,
):
    """Get canonical name using the selected API with sequel preservation."""
    import re

    def preserve_sequel_numbers(original_name, api_name):
        """Preserve numbered sequels when API returns generic name."""
        # Extract numbers from the original name
        original_numbers = re.findall(r"\b\d+\b", original_name)
        api_numbers = re.findall(r"\b\d+\b", api_name)

        # If original has numbers but API result doesn't, preserve the original
        if original_numbers and not api_numbers:
            return original_name

        # If original has NO numbers but API result DOES have numbers, preserve the original
        # (API likely returned wrong sequel for the base game)
        if not original_numbers and api_numbers:
            return original_name

        # If both have numbers but they're different, preserve the original
        if original_numbers and api_numbers and original_numbers != api_numbers:
            return original_name

        return api_name

    if api_choice == "thegamesdb":
        api_result = get_canonical_name(game_name, file_extension, tgdb_api_key, logger)
        return preserve_sequel_numbers(game_name, api_result)
    elif api_choice == "igdb":
        # Use the original IGDB logic from rom_cleanup.py
        if query_igdb_game and igdb_client_id and igdb_access_token:
            # Set global variables in rom_cleanup module before calling
            import rom_cleanup

            rom_cleanup.IGDB_CLIENT_ID = igdb_client_id
            rom_cleanup.IGDB_ACCESS_TOKEN = igdb_access_token
            result = query_igdb_game(game_name, file_extension)
            if result:
                api_result = result.get("canonical_name", game_name)
                return preserve_sequel_numbers(game_name, api_result)

    # Fallback to original name
    return game_name


# Platform mapping for file extensions to console IDs
# This helps match ROMs to their correct platforms
PLATFORM_MAPPING = {
    # PlayStation
    "cue": [7],  # PlayStation
    "bin": [7],  # PlayStation
    "img": [7],  # PlayStation
    "iso": [7, 8, 9],  # PlayStation 1/2/3
    "pbp": [13],  # PlayStation Portable
    # Nintendo
    "nes": [4],  # Nintendo Entertainment System
    "smc": [5],  # Super Nintendo
    "sfc": [5],  # Super Nintendo
    "n64": [3],  # Nintendo 64
    "z64": [3],  # Nintendo 64
    "v64": [3],  # Nintendo 64
    "gb": [4],  # Game Boy
    "gbc": [41],  # Game Boy Color
    "gba": [12],  # Game Boy Advance
    "nds": [20],  # Nintendo DS
    "3ds": [37],  # Nintendo 3DS
    # Sega
    "smd": [18],  # Sega Mega Drive/Genesis
    "gen": [18],  # Sega Genesis
    "sms": [35],  # Sega Master System
    "gg": [21],  # Sega Game Gear
    "32x": [33],  # Sega 32X
    "cdi": [23, 16],  # Sega CD and Dreamcast
    "sat": [17],  # Sega Saturn
    # Other
    "zip": [],  # Generic archive
    "7z": [],  # Generic archive
    "rar": [],  # Generic archive
}


# Setup logging for GUI
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class ROMCleanupGUI:
    """Main GUI application class."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("ROM Collection Cleanup Tool")
        self.root.geometry("1200x900")
        self.root.minsize(1000, 700)

        # Create main frame with dark theme
        main_frame = ttk.Frame(root, padding="20", style="Dark.TFrame")
        main_frame.grid(
            row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10
        )

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)  # Give weight to the log frame

        # Variables
        self.directory_var = tk.StringVar()
        self.region_var = tk.StringVar(value="usa")
        self.keep_japanese_var = tk.BooleanVar(value=True)
        self.operation_var = tk.StringVar(value="move")
        self.progress_var = tk.DoubleVar()
        self.status_var = tk.StringVar(value="Ready")

        # API credentials - dual system
        self.api_choice = tk.StringVar(
            value="igdb"
        )  # Default to IGDB (superior database)
        self.tgdb_api_key = tk.StringVar()
        self.igdb_client_id = tk.StringVar()
        self.igdb_access_token = tk.StringVar()

        # API status tracking
        self.api_status_var = tk.StringVar(value="Not configured")
        self.api_status_color = tk.StringVar(value="#ff6b6b")  # Red by default

        # Processing control
        self.current_process = None
        self.process_stop_requested = False

        # Setup GUI
        self.setup_gui(main_frame)

        # Load any saved credentials
        self.load_saved_credentials()

    def setup_gui(self, parent: ttk.Frame) -> None:
        """Set up the GUI elements."""
        # Create notebook for tabs with dark theme
        notebook = ttk.Notebook(parent, style="Dark.TNotebook")
        notebook.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20))

        # Main tab
        main_frame = ttk.Frame(notebook, padding="20", style="Dark.TFrame")
        notebook.add(main_frame, text="Main")

        # Advanced tab
        advanced_frame = ttk.Frame(notebook, padding="20", style="Dark.TFrame")
        notebook.add(advanced_frame, text="Advanced Settings")

        # Setup main tab
        self.setup_main_tab(main_frame)

        # Setup advanced tab
        self.setup_advanced_tab(advanced_frame)

        # Status and progress section
        status_frame = ttk.Frame(parent, style="Dark.TFrame")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(20, 0))
        status_frame.columnconfigure(1, weight=1)

        # Status label
        ttk.Label(status_frame, text="Status:", style="Dark.TLabel").grid(
            row=0, column=0, sticky=tk.W
        )
        status_label = ttk.Label(
            status_frame, textvariable=self.status_var, style="Dark.TLabel"
        )
        status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            status_frame,
            variable=self.progress_var,
            maximum=100,
            style="Dark.Horizontal.TProgressbar",
        )
        self.progress_bar.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0)
        )

        # Log display
        log_frame = ttk.LabelFrame(
            parent, text="Console Output", padding="15", style="Dark.TLabelframe"
        )
        log_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(20, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        # Create a custom dark themed scrolled text
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="#2d2d2d",
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground="#64b5f6",
            selectforeground="white",
            font=("Consolas", 9),
            borderwidth=1,
            relief="solid",
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Control buttons
        button_frame = ttk.Frame(parent, style="Dark.TFrame")
        button_frame.grid(row=3, column=0, pady=(20, 0))

        ttk.Button(
            button_frame,
            text="Start Scan",
            command=self.start_scan,
            style="Primary.TButton",
        ).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(
            button_frame, text="Stop", command=self.stop_process, style="Dark.TButton"
        ).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(
            button_frame, text="Clear Log", command=self.clear_log, style="Dark.TButton"
        ).grid(row=0, column=2)

    def setup_main_tab(self, parent):
        """Set up the main tab elements."""
        # Directory selection section
        dir_section = ttk.LabelFrame(
            parent, text="ROM Directory", padding="15", style="Dark.TLabelframe"
        )
        dir_section.grid(
            row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20)
        )
        dir_section.columnconfigure(0, weight=1)

        ttk.Label(
            dir_section,
            text="Select the directory containing your ROM files:",
            style="Dark.TLabel",
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        dir_frame = ttk.Frame(dir_section, style="Dark.TFrame")
        dir_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        dir_frame.columnconfigure(0, weight=1)

        ttk.Entry(
            dir_frame, textvariable=self.directory_var, width=60, style="Dark.TEntry"
        ).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        ttk.Button(
            dir_frame,
            text="Browse",
            command=self.browse_directory,
            style="Dark.TButton",
        ).grid(row=0, column=1)

        # Region preference section
        region_section = ttk.LabelFrame(
            parent, text="Region Preference", padding="15", style="Dark.TLabelframe"
        )
        region_section.grid(
            row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20)
        )

        ttk.Label(
            region_section,
            text="Choose your preferred region when multiple versions exist:",
            style="Dark.TLabel",
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        region_frame = ttk.Frame(region_section, style="Dark.TFrame")
        region_frame.grid(row=1, column=0, sticky=tk.W)

        ttk.Radiobutton(
            region_frame,
            text="USA",
            variable=self.region_var,
            value="usa",
            style="Dark.TRadiobutton",
        ).grid(row=0, column=0, padx=(0, 20), sticky=tk.W)
        ttk.Radiobutton(
            region_frame,
            text="Europe",
            variable=self.region_var,
            value="europe",
            style="Dark.TRadiobutton",
        ).grid(row=0, column=1, padx=(0, 20), sticky=tk.W)
        ttk.Radiobutton(
            region_frame,
            text="Japan",
            variable=self.region_var,
            value="japan",
            style="Dark.TRadiobutton",
        ).grid(row=0, column=2, sticky=tk.W)

        # Options section
        options_section = ttk.LabelFrame(
            parent, text="Options", padding="15", style="Dark.TLabelframe"
        )
        options_section.grid(
            row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20)
        )

        ttk.Checkbutton(
            options_section,
            text="Keep Japanese-only games (games with no USA/Europe release)",
            variable=self.keep_japanese_var,
            style="Dark.TCheckbutton",
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        # Operation mode section
        operation_section = ttk.LabelFrame(
            parent, text="Operation Mode", padding="15", style="Dark.TLabelframe"
        )
        operation_section.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))

        ttk.Label(
            operation_section,
            text="What should happen to duplicate files?",
            style="Dark.TLabel",
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))

        op_frame = ttk.Frame(operation_section, style="Dark.TFrame")
        op_frame.grid(row=1, column=0, sticky=tk.W)

        ttk.Radiobutton(
            op_frame,
            text="Move files to subdirectory",
            variable=self.operation_var,
            value="move",
            style="Dark.TRadiobutton",
        ).grid(row=0, column=0, padx=(0, 20), sticky=tk.W)
        ttk.Radiobutton(
            op_frame,
            text="Delete files permanently",
            variable=self.operation_var,
            value="delete",
            style="Dark.TRadiobutton",
        ).grid(row=0, column=1, sticky=tk.W)

    def setup_advanced_tab(self, parent):
        """Set up the advanced settings tab with dual API support."""
        # API Choice section
        choice_section = ttk.LabelFrame(
            parent, text="Database Selection", padding="20", style="Dark.TLabelframe"
        )
        choice_section.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        choice_section.columnconfigure(0, weight=1)

        ttk.Label(
            choice_section,
            text="Choose your preferred game database for enhanced ROM matching:",
            style="Dark.TLabel",
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        # Radio buttons for API choice
        api_choice_frame = ttk.Frame(choice_section, style="Dark.TFrame")
        api_choice_frame.grid(row=1, column=0, sticky=tk.W, pady=(0, 10))

        ttk.Radiobutton(
            api_choice_frame,
            text="TheGamesDB (Recommended for ROM collectors)",
            variable=self.api_choice,
            value="thegamesdb",
            style="Dark.TRadiobutton",
            command=self.on_api_choice_changed,
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        ttk.Radiobutton(
            api_choice_frame,
            text="IGDB (No Discord required)",
            variable=self.api_choice,
            value="igdb",
            style="Dark.TRadiobutton",
            command=self.on_api_choice_changed,
        ).grid(row=1, column=0, sticky=tk.W)

        # TheGamesDB Configuration section
        self.tgdb_section = ttk.LabelFrame(
            parent,
            text="TheGamesDB Configuration",
            padding="20",
            style="Dark.TLabelframe",
        )
        self.tgdb_section.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        self.tgdb_section.columnconfigure(0, weight=1)

        # TGDB description
        tgdb_desc = (
            "ROM-focused database with excellent cross-language matching.\n"
            "Requires Discord access to request API key."
        )
        ttk.Label(
            self.tgdb_section, text=tgdb_desc, style="Dark.TLabel", wraplength=600
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        # TGDB API Key input
        tgdb_key_frame = ttk.Frame(self.tgdb_section, style="Dark.TFrame")
        tgdb_key_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        tgdb_key_frame.columnconfigure(1, weight=1)

        ttk.Label(tgdb_key_frame, text="API Key:", style="Dark.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        self.tgdb_entry = ttk.Entry(
            tgdb_key_frame,
            textvariable=self.tgdb_api_key,
            width=50,
            show="*",
            style="Dark.TEntry",
        )
        self.tgdb_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # IGDB Configuration section
        self.igdb_section = ttk.LabelFrame(
            parent, text="IGDB Configuration", padding="20", style="Dark.TLabelframe"
        )
        self.igdb_section.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        self.igdb_section.columnconfigure(0, weight=1)

        # IGDB description
        igdb_desc = (
            "Comprehensive game database with detailed metadata.\n"
            "No Discord required - get credentials via Twitch Developer Console."
        )
        ttk.Label(
            self.igdb_section, text=igdb_desc, style="Dark.TLabel", wraplength=600
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        # IGDB Client ID input
        igdb_id_frame = ttk.Frame(self.igdb_section, style="Dark.TFrame")
        igdb_id_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        igdb_id_frame.columnconfigure(1, weight=1)

        ttk.Label(igdb_id_frame, text="Client ID:", style="Dark.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        self.igdb_id_entry = ttk.Entry(
            igdb_id_frame,
            textvariable=self.igdb_client_id,
            width=50,
            style="Dark.TEntry",
        )
        self.igdb_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # IGDB Access Token input
        igdb_token_frame = ttk.Frame(self.igdb_section, style="Dark.TFrame")
        igdb_token_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        igdb_token_frame.columnconfigure(1, weight=1)

        ttk.Label(igdb_token_frame, text="Access Token:", style="Dark.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        self.igdb_token_entry = ttk.Entry(
            igdb_token_frame,
            textvariable=self.igdb_access_token,
            width=50,
            show="*",
            style="Dark.TEntry",
        )
        self.igdb_token_entry.grid(row=0, column=1, sticky=(tk.W, tk.E))

        # Status and buttons section
        status_section = ttk.Frame(parent, style="Dark.TFrame")
        status_section.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        status_section.columnconfigure(0, weight=1)

        # API Status indicator
        status_frame = ttk.Frame(status_section, style="Dark.TFrame")
        status_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))

        ttk.Label(status_frame, text="Status:", style="Dark.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10)
        )
        self.api_status_label = ttk.Label(
            status_frame, textvariable=self.api_status_var, style="Dark.TLabel"
        )
        self.api_status_label.grid(row=0, column=1, sticky=tk.W)

        # API management buttons
        button_frame = ttk.Frame(status_section, style="Dark.TFrame")
        button_frame.grid(row=1, column=0, sticky=tk.W)

        ttk.Button(
            button_frame,
            text="Test Connection",
            command=self.show_api_details,
            style="Primary.TButton",
        ).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="Save Credentials",
            command=self.save_current_credentials,
            style="Dark.TButton",
        ).grid(row=0, column=1, padx=(0, 10))

        ttk.Button(
            button_frame,
            text="Generate IGDB Token",
            command=self.launch_token_generator,
            style="Dark.TButton",
        ).grid(row=0, column=2)

        # Bind validation to credential changes
        self.tgdb_api_key.trace("w", lambda *args: self.validate_api_credentials())
        self.igdb_client_id.trace("w", lambda *args: self.validate_api_credentials())
        self.igdb_access_token.trace("w", lambda *args: self.validate_api_credentials())

        # Initial state setup
        self.on_api_choice_changed()

    def on_api_choice_changed(self):
        """Handle API choice changes - show/hide appropriate sections."""
        choice = self.api_choice.get()

        if choice == "thegamesdb":
            # Show TGDB section, hide IGDB section
            self.tgdb_section.grid()
            self.igdb_section.grid_remove()
        else:  # igdb
            # Show IGDB section, hide TGDB section
            self.igdb_section.grid()
            self.tgdb_section.grid_remove()

        # Revalidate credentials
        self.validate_api_credentials()

    def launch_token_generator(self):
        """Launch the integrated IGDB token generator dialog."""
        self.show_token_generator_dialog()

    def show_token_generator_dialog(self):
        """Show the integrated IGDB token generator dialog."""
        # Create the dialog window
        dialog = tk.Toplevel(self.root)
        dialog.title("IGDB Token Generator")
        dialog.geometry("600x500")
        dialog.configure(bg="#1e1e1e")
        dialog.resizable(True, True)

        # Make it modal
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"+{x}+{y}")

        # Setup dark theme for dialog
        dialog_style = ttk.Style()
        dialog_style.theme_use("clam")

        # Main frame
        main_frame = ttk.Frame(dialog, padding="20", style="Dark.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dialog.columnconfigure(0, weight=1)
        dialog.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame, text="IGDB Token Generator", style="Heading.TLabel"
        )
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)

        # Instructions
        instructions = (
            "This tool will help you generate IGDB credentials using the Twitch OAuth2 flow.\n\n"
            "You'll need:\n"
            "1. IGDB Client ID (from Twitch Developer Console)\n"
            "2. IGDB Client Secret (from Twitch Developer Console)\n\n"
            "The tool will generate an Access Token for you to use with the ROM Cleanup Tool."
        )

        inst_label = ttk.Label(
            main_frame, text=instructions, style="Dark.TLabel", wraplength=550
        )
        inst_label.grid(row=1, column=0, pady=(0, 20), sticky=(tk.W, tk.E))

        # Input fields
        input_frame = ttk.LabelFrame(
            main_frame,
            text="Enter Your IGDB Credentials",
            padding="15",
            style="Dark.TLabelframe",
        )
        input_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        input_frame.columnconfigure(1, weight=1)

        # Client ID
        ttk.Label(input_frame, text="Client ID:", style="Dark.TLabel").grid(
            row=0, column=0, sticky=tk.W, padx=(0, 10), pady=(0, 10)
        )
        client_id_var = tk.StringVar()
        client_id_entry = ttk.Entry(
            input_frame, textvariable=client_id_var, width=50, style="Dark.TEntry"
        )
        client_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 10))

        # Client Secret
        ttk.Label(input_frame, text="Client Secret:", style="Dark.TLabel").grid(
            row=1, column=0, sticky=tk.W, padx=(0, 10)
        )
        client_secret_var = tk.StringVar()
        client_secret_entry = ttk.Entry(
            input_frame,
            textvariable=client_secret_var,
            width=50,
            show="*",
            style="Dark.TEntry",
        )
        client_secret_entry.grid(row=1, column=1, sticky=(tk.W, tk.E))

        # Output area
        output_frame = ttk.LabelFrame(
            main_frame, text="Output", padding="15", style="Dark.TLabelframe"
        )
        output_frame.grid(
            row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 20)
        )
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)

        # Output text widget
        output_text = scrolledtext.ScrolledText(
            output_frame,
            height=8,
            width=70,
            bg="#2d2d2d",
            fg="#ffffff",
            selectbackground="#64b5f6",
            selectforeground="white",
            insertbackground="#ffffff",
            font=("Consolas", 9),
        )
        output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Button frame
        button_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        button_frame.grid(row=4, column=0, sticky=(tk.W, tk.E))

        def generate_token():
            """Generate the IGDB token and display results."""
            client_id = client_id_var.get().strip()
            client_secret = client_secret_var.get().strip()

            if not client_id or not client_secret:
                output_text.insert(
                    tk.END, "ERROR: Both Client ID and Client Secret are required\n"
                )
                return

            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, "IGDB Access Token Generator\n")
            output_text.insert(tk.END, "=" * 40 + "\n\n")

            output_text.insert(tk.END, f"Client ID: {client_id[:8]}...\n")
            output_text.insert(tk.END, f"Client Secret: {client_secret[:8]}...\n\n")

            # Generate token using IGDB token logic
            token_data = self.get_igdb_token_internal(
                client_id, client_secret, output_text
            )

            if token_data:
                access_token = token_data.get("access_token")

                # Test the token
                success = self.test_igdb_connection_internal(
                    client_id, access_token, output_text
                )

                if success:
                    output_text.insert(
                        tk.END, "\n🎉 SUCCESS: Your IGDB setup is working!\n\n"
                    )
                    output_text.insert(tk.END, "✅ Generated credentials:\n")
                    output_text.insert(tk.END, f"   Client ID: {client_id}\n")
                    output_text.insert(tk.END, f"   Access Token: {access_token}\n\n")

                    # Auto-populate the main GUI fields
                    self.igdb_client_id.set(client_id)
                    self.igdb_access_token.set(access_token)

                    output_text.insert(
                        tk.END,
                        "✨ Credentials have been automatically filled in the main GUI!\n",
                    )
                    output_text.insert(
                        tk.END,
                        "   You can close this window and test the connection.\n\n",
                    )

                    expires_in = token_data.get("expires_in", 0)
                    if expires_in > 0:
                        hours = expires_in // 3600
                        output_text.insert(
                            tk.END,
                            f"⏰ Note: This token expires in {expires_in} seconds ({hours:.1f} hours)\n",
                        )
                        output_text.insert(
                            tk.END,
                            "   You'll need to generate a new token when it expires.\n",
                        )
                else:
                    output_text.insert(
                        tk.END,
                        "\n❌ IGDB API test failed. Please check your credentials.\n",
                    )
            else:
                output_text.insert(
                    tk.END,
                    "\n❌ Failed to get access token. Please check your credentials.\n",
                )

            output_text.see(tk.END)

        def close_dialog():
            """Close the dialog window."""
            dialog.grab_release()
            dialog.destroy()

        # Buttons
        ttk.Button(
            button_frame,
            text="Generate Token",
            command=generate_token,
            style="Primary.TButton",
        ).grid(row=0, column=0, padx=(0, 10))

        ttk.Button(
            button_frame, text="Close", command=close_dialog, style="Dark.TButton"
        ).grid(row=0, column=1)

        # Focus on first input
        client_id_entry.focus()

    def get_igdb_token_internal(self, client_id, client_secret, output_widget):
        """Internal method to get IGDB token."""
        if not requests:
            output_widget.insert(tk.END, "ERROR: requests library not available\n")
            return None

        url = "https://id.twitch.tv/oauth2/token"
        params = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }

        try:
            output_widget.insert(tk.END, "Requesting access token from Twitch...\n")
            output_widget.update()

            response = requests.post(url, params=params, timeout=10)

            if response.status_code == 200:
                token_data = response.json()
                output_widget.insert(tk.END, "SUCCESS: Access token obtained!\n")

                expires_in = token_data.get("expires_in", 0)
                token_type = token_data.get("token_type", "unknown")

                output_widget.insert(
                    tk.END, f"   Token expires in: {expires_in} seconds\n"
                )
                output_widget.insert(tk.END, f"   Token type: {token_type}\n")

                if expires_in > 0:
                    from datetime import datetime, timedelta

                    expiration_time = datetime.now() + timedelta(seconds=expires_in)
                    output_widget.insert(
                        tk.END,
                        f"   Expires at: {expiration_time.strftime('%Y-%m-%d %H:%M:%S')}\n",
                    )

                return token_data
            else:
                output_widget.insert(tk.END, "ERROR: Failed to get access token\n")
                output_widget.insert(
                    tk.END, f"   Status code: {response.status_code}\n"
                )
                output_widget.insert(tk.END, f"   Response: {response.text}\n")
                return None

        except Exception as e:
            output_widget.insert(tk.END, f"ERROR: {e}\n")
            return None

    def test_igdb_connection_internal(self, client_id, access_token, output_widget):
        """Internal method to test IGDB connection."""
        if not requests:
            output_widget.insert(tk.END, "ERROR: requests library not available\n")
            return False

        url = "https://api.igdb.com/v4/games"
        headers = {
            "Client-ID": client_id,
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        }
        query = "fields name; limit 1;"

        try:
            output_widget.insert(tk.END, "\nTesting IGDB API connection...\n")
            output_widget.update()

            response = requests.post(url, headers=headers, data=query, timeout=10)

            if response.status_code == 200:
                games = response.json()
                output_widget.insert(tk.END, "SUCCESS: IGDB API connection working!\n")
                output_widget.insert(tk.END, f"   Found {len(games)} test game(s)\n")
                if games:
                    output_widget.insert(
                        tk.END, f"   Sample game: {games[0].get('name', 'Unknown')}\n"
                    )
                return True
            else:
                output_widget.insert(tk.END, "ERROR: IGDB API test failed\n")
                output_widget.insert(
                    tk.END, f"   Status code: {response.status_code}\n"
                )
                output_widget.insert(tk.END, f"   Response: {response.text}\n")
                return False

        except Exception as e:
            output_widget.insert(tk.END, f"ERROR: {e}\n")
            return False

    def browse_directory(self) -> None:
        """Open directory browser with validation."""
        try:
            directory = filedialog.askdirectory(
                title="Select ROM Directory", mustexist=True
            )
            if directory:
                # Validate the selected directory
                directory_path = Path(directory)
                if not directory_path.exists():
                    messagebox.showerror("Error", "Selected directory does not exist")
                    return
                if not directory_path.is_dir():
                    messagebox.showerror("Error", "Selected path is not a directory")
                    return

                self.directory_var.set(str(directory_path))
                logger.info(f"Selected directory: {directory_path}")
        except Exception as e:
            logger.error(f"Error browsing directory: {e}")
            messagebox.showerror("Error", f"Failed to select directory: {e}")

    def log_message(self, message: str) -> None:
        """Add a message to the log display with timestamp.

        Args:
            message: The message to log
        """
        try:
            timestamp = datetime.now().strftime("%H:%M:%S")
            formatted_message = f"[{timestamp}] {message}\n"

            # Safely update the text widget
            if hasattr(self, "log_text") and self.log_text.winfo_exists():
                self.log_text.config(state=tk.NORMAL)
                self.log_text.insert(tk.END, formatted_message)
                self.log_text.see(tk.END)
                self.log_text.config(state=tk.DISABLED)
            else:
                # Fallback to logger if widget doesn't exist
                logger.info(message)

            # Copy to clipboard if available and it's a file path
            if CLIPBOARD_AVAILABLE and (
                "Duplicate" in message or "Remove" in message or "Delete" in message
            ):
                try:
                    pyperclip.copy(message)
                except Exception as e:
                    logger.debug(f"Clipboard operation failed: {e}")
        except Exception as e:
            logger.error(f"Error logging message: {e}")

    def clear_log(self):
        """Clear the log display."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def check_api_connection(self):
        """Check API connection based on selected API type"""
        api_choice = self.api_choice.get()

        if not requests:
            return False, "requests library not available"

        if api_choice == "thegamesdb":
            return self._check_tgdb_connection()
        elif api_choice == "igdb":
            return self._check_igdb_connection()
        else:
            return False, "No API selected"

    def _check_tgdb_connection(self):
        """Check TheGamesDB API connection"""
        tgdb_api_key = self.tgdb_api_key.get().strip()

        if not tgdb_api_key:
            return False, "TheGamesDB API Key not configured"

        try:
            response = requests.get(
                f"https://api.thegamesdb.net/v1/Games/ByGameName?apikey={tgdb_api_key}&name=Mario&fields=games",
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                if data.get("data") and data["data"].get("games"):
                    return True, "TheGamesDB connection successful"
                else:
                    return False, "TheGamesDB connected but no valid response data"
            elif response.status_code == 401:
                return False, "TheGamesDB authentication failed - check API Key"
            elif response.status_code == 429:
                return False, "TheGamesDB rate limit exceeded - wait a few minutes"
            else:
                return (
                    False,
                    f"TheGamesDB test failed - response code: {response.status_code}",
                )

        except requests.exceptions.ConnectionError as e:
            return False, f"TheGamesDB connection error: {e}"
        except requests.exceptions.Timeout as e:
            return False, f"TheGamesDB request timeout: {e}"
        except Exception as e:
            return False, f"TheGamesDB error: {e}"

    def _check_igdb_connection(self):
        """Check IGDB API connection"""
        client_id = self.igdb_client_id.get().strip()
        access_token = self.igdb_access_token.get().strip()

        if not client_id:
            return False, "IGDB Client ID not configured"
        if not access_token:
            return False, "IGDB Access Token not configured"

        try:
            headers = {
                "Client-ID": client_id,
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            }
            response = requests.post(
                "https://api.igdb.com/v4/games",
                headers=headers,
                data="fields name; limit 1;",
                timeout=10,
            )

            if response.status_code == 200:
                return True, "IGDB connection successful"
            elif response.status_code == 401:
                return False, "IGDB authentication failed - check credentials"
            elif response.status_code == 429:
                return False, "IGDB rate limit exceeded - wait a few minutes"
            else:
                return (
                    False,
                    f"IGDB test failed - response code: {response.status_code}",
                )

        except requests.exceptions.ConnectionError as e:
            return False, f"IGDB connection error: {e}"
        except requests.exceptions.Timeout as e:
            return False, f"IGDB request timeout: {e}"
        except Exception as e:
            return False, f"IGDB error: {e}"

    def validate_api_credentials(self) -> None:
        """Validate API credentials and update status."""
        try:
            api_choice = self.api_choice.get()

            # Check if we have any credentials for the selected API
            has_credentials = False
            if api_choice == "thegamesdb":
                api_key = self.tgdb_api_key.get().strip()
                has_credentials = bool(api_key and len(api_key) > 5)  # Basic validation
            elif api_choice == "igdb":
                client_id = self.igdb_client_id.get().strip()
                access_token = self.igdb_access_token.get().strip()
                has_credentials = bool(
                    client_id
                    and access_token
                    and len(client_id) > 5
                    and len(access_token) > 10
                )
            else:
                logger.warning(f"Unknown API choice: {api_choice}")
                has_credentials = False

            if not has_credentials:
                self._update_api_status("Not configured", "#ff6b6b")  # Red
                return

            # Test the connection
            self._test_api_connection()
        except Exception as e:
            logger.error(f"Error validating API credentials: {e}")
            self._update_api_status("Validation error", "#ff6b6b")

    def _update_api_status(self, status: str, color: str) -> None:
        """Update the API status display safely.

        Args:
            status: Status message to display
            color: Color for the status text
        """
        try:
            self.api_status_var.set(status)
            self.api_status_color.set(color)
            if (
                hasattr(self, "api_status_label")
                and self.api_status_label.winfo_exists()
            ):
                self.api_status_label.config(text=status, foreground=color)
        except Exception as e:
            logger.error(f"Error updating API status: {e}")

    def _test_api_connection(self) -> None:
        """Test the API connection and update status."""
        try:
            success, message = self.check_api_connection()
            if success:
                self._update_api_status("Connected", "#4CAF50")  # Green
                # Auto-save credentials when connection is successful
                self.save_current_credentials()
            else:
                # Show the specific error message
                error_text = f"{message}"
                if len(error_text) > 50:  # Truncate long error messages
                    error_text = error_text[:47] + "..."
                self._update_api_status(f"Error: {error_text}", "#ff6b6b")  # Red
        except Exception as e:
            logger.error(f"Error testing API connection: {e}")
            self._update_api_status("Connection test failed", "#ff6b6b")

        # Update the status label if it exists
        if hasattr(self, "api_status_label"):
            self.api_status_label.config(
                text=self.api_status_var.get(), foreground=self.api_status_color.get()
            )

    def load_saved_credentials(self):
        """Load saved API credentials and populate the fields"""
        try:
            credentials = load_api_credentials()

            # Set API choice
            self.api_choice.set(credentials["api_choice"])

            # Set credentials
            if credentials["tgdb_api_key"]:
                self.tgdb_api_key.set(credentials["tgdb_api_key"])
            if credentials["igdb_client_id"]:
                self.igdb_client_id.set(credentials["igdb_client_id"])
            if credentials["igdb_access_token"]:
                self.igdb_access_token.set(credentials["igdb_access_token"])

            if any(credentials.values()):
                self.log_message("Loaded saved API credentials")
                # Update UI based on choice
                self.on_api_choice_changed()
                # Validate the loaded credentials
                self.validate_api_credentials()
        except Exception as e:
            self.log_message(f"Error loading credentials: {e}")

    def save_current_credentials(self):
        """Save current API credentials to file"""
        api_choice = self.api_choice.get()
        tgdb_api_key = self.tgdb_api_key.get().strip()
        igdb_client_id = self.igdb_client_id.get().strip()
        igdb_access_token = self.igdb_access_token.get().strip()

        # Check if we have credentials for the selected API
        has_credentials = False
        if api_choice == "thegamesdb" and tgdb_api_key:
            has_credentials = True
        elif api_choice == "igdb" and igdb_client_id and igdb_access_token:
            has_credentials = True

        if has_credentials:
            if save_api_credentials(
                api_choice, tgdb_api_key, igdb_client_id, igdb_access_token
            ):
                self.log_message("API credentials saved successfully")
                return True
            else:
                self.log_message("Failed to save API credentials")
                return False
        else:
            self.log_message("No credentials to save for selected API")
            return False

    def show_api_details(self):
        """Show detailed API connection information"""
        tgdb_api_key = self.tgdb_api_key.get().strip()

        self.log_message("\n" + "=" * 50)
        self.log_message("DETAILED API CONNECTION INFO")
        self.log_message("=" * 50)

        # Show credential status (masked)
        if tgdb_api_key:
            masked_key = (
                tgdb_api_key[:4] + "*" * (len(tgdb_api_key) - 8) + tgdb_api_key[-4:]
                if len(tgdb_api_key) > 8
                else "****"
            )
            self.log_message(f"TGDB API Key: {masked_key}")
        else:
            self.log_message("TGDB API Key: NOT SET")

        # Test connection and show detailed results
        if not tgdb_api_key:
            self.log_message("ERROR: Missing API key")
            return

        if not requests:
            self.log_message("ERROR: requests library not available")
            return

        try:
            self.log_message("Testing connection to TheGamesDB API...")
            # Test with a simple request to get a single game
            response = requests.get(
                f"https://api.thegamesdb.net/v1/Games/ByGameName?apikey={tgdb_api_key}&name=Mario&fields=games",
                timeout=10,
            )

            self.log_message(f"Response Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if data.get("data") and data["data"].get("games"):
                    self.log_message("SUCCESS: API connection successful!")
                    self.log_message("Your API key is working correctly.")
                    # Auto-save credentials on successful connection
                    self.save_current_credentials()
                else:
                    self.log_message("WARNING: API responded but no games found")
                    self.log_message(
                        "API key appears to be working but query returned no results"
                    )
            elif response.status_code == 401:
                self.log_message("ERROR: Authentication failed (401)")
                self.log_message("This usually means:")
                self.log_message("  - API Key is incorrect")
                self.log_message("  - API Key has expired or been revoked")
            elif response.status_code == 429:
                self.log_message("ERROR: Rate limit exceeded (429)")
                self.log_message("Too many requests - wait a moment and try again")
            else:
                self.log_message(f"ERROR: Unexpected response: {response.status_code}")
                self.log_message(f"Response text: {response.text[:200]}...")

        except requests.exceptions.ConnectionError as e:
            self.log_message(f"ERROR: Connection error: {e}")
            self.log_message("Check your internet connection")
        except requests.exceptions.Timeout as e:
            self.log_message(f"ERROR: Request timeout: {e}")
            self.log_message("The API request took too long")
        except Exception as e:
            self.log_message(f"ERROR: Unexpected error: {e}")

        self.log_message("=" * 50)

    def stop_process(self):
        """Stop current process without closing the app"""
        if self.current_process and self.current_process.is_alive():
            self.process_stop_requested = True
            self.log_message(
                "STOP: Stop requested - waiting for current operation to complete..."
            )
        else:
            self.log_message("No running process to stop")

    def start_scan(self):
        """Start the ROM scanning process."""
        directory = self.directory_var.get().strip()
        if not directory:
            messagebox.showerror("Error", "Please select a ROM directory.")
            return

        if not Path(directory).exists():
            messagebox.showerror("Error", "Selected directory does not exist.")
            return

        # Reset stop flag
        self.process_stop_requested = False

        # Start processing in a separate thread
        self.current_process = threading.Thread(
            target=self.scan_roms,
            args=(
                directory,
                self.region_var.get(),
                self.keep_japanese_var.get(),
                self.operation_var.get(),
            ),
        )
        self.current_process.start()

    def scan_roms(self, directory, preferred_region, keep_japanese_only, operation):
        """Scan ROMs and identify duplicates."""
        try:
            self.status_var.set("Scanning ROMs...")
            self.progress_var.set(0)

            self.log_message(f"Scanning directory: {directory}")
            self.log_message(f"Operation mode: {operation}")
            self.log_message(f"Preferred region: {preferred_region}")
            self.log_message(f"Keep Japanese-only: {keep_japanese_only}")

            # Check API status
            success, message = self.check_api_connection()
            if success:
                self.log_message("SUCCESS: API connection successful")
                self.log_message("Enhanced game matching is available")
            else:
                self.log_message(f"WARNING: {message}")
                self.log_message("Using basic filename matching only")

            # Find all ROM files
            rom_files = []
            rom_extensions = {
                ".zip",
                ".7z",
                ".rar",
                ".iso",
                ".cue",
                ".bin",
                ".img",
                ".smc",
                ".sfc",
                ".nes",
                ".n64",
                ".z64",
                ".v64",
                ".gb",
                ".gbc",
                ".gba",
                ".nds",
                ".3ds",
                ".smd",
                ".gen",
                ".sms",
                ".gg",
                ".32x",
                ".cdi",
                ".sat",
                ".pbp",
                ".cso",
            }

            for ext in rom_extensions:
                rom_files.extend(Path(directory).glob(f"**/*{ext}"))

            if not rom_files:
                self.log_message("No ROM files found!")
                self.status_var.set("No ROMs found")
                return

            total_files = len(rom_files)
            self.log_message(f"Found {total_files} ROM files")

            # Group ROMs by canonical name
            rom_groups = defaultdict(list)

            for i, file_path in enumerate(rom_files):
                # Check if stop was requested
                if self.process_stop_requested:
                    self.log_message("STOP: Process stopped by user request")
                    self.status_var.set("Stopped")
                    return

                filename = file_path.name
                base_name = get_base_name(filename)
                region = get_region(filename)
                file_extension = file_path.suffix.lower()

                # Log progress every 100 files or if it's one of the first 10
                if i < 10 or (i + 1) % 100 == 0:
                    self.log_message(f"[{i+1}/{total_files}] Processing: {filename}")
                    self.log_message(f"   Base name: {base_name}")
                    self.log_message(f"   Region: {region}")

                # Get user credentials for API calls
                api_choice = self.api_choice.get()
                tgdb_api_key = self.tgdb_api_key.get().strip()
                igdb_client_id = self.igdb_client_id.get().strip()
                igdb_access_token = self.igdb_access_token.get().strip()

                canonical_name = get_unified_canonical_name(
                    base_name,
                    file_extension,
                    api_choice,
                    tgdb_api_key,
                    igdb_client_id,
                    igdb_access_token,
                    logger=self.log_message,
                )

                # Debug logging for canonical name assignment
                if base_name != canonical_name:
                    self.log_message(
                        f"   Canonical name: '{base_name}' -> '{canonical_name}'"
                    )
                else:
                    self.log_message(f"   Canonical name: '{canonical_name}'")

                rom_groups[canonical_name].append((file_path, region, base_name))

                # Update progress
                progress = ((i + 1) / total_files) * 100
                self.progress_var.set(progress)
                self.root.update_idletasks()

            # Process groups and identify duplicates
            self.status_var.set("Analyzing duplicates...")
            self.process_duplicates(
                rom_groups, preferred_region, keep_japanese_only, operation
            )

        except Exception as e:
            self.log_message(f"Error during scan: {e}")
            self.status_var.set("Error occurred")

    def process_duplicates(
        self, rom_groups, preferred_region, keep_japanese_only, operation
    ):
        """Process ROM groups and handle duplicates using ENHANCED logic (cross-regional + same-region)."""
        from rom_cleanup import find_duplicates_to_remove

        total_groups = len(rom_groups)
        self.log_message(
            f"\nAnalyzing {total_groups} game groups with ENHANCED duplicate detection..."
        )

        # Use the ENHANCED duplicate detection logic from rom_cleanup.py
        try:
            to_remove = find_duplicates_to_remove(rom_groups, self.log_message)
            removed_count = len(to_remove)

            self.log_message("\n✅ Analysis complete!")
            self.log_message(f"📊 Groups analyzed: {total_groups}")
            self.log_message(
                f"🎯 Duplicates found (cross-regional + same-region): {removed_count}"
            )
            self.log_message(
                f"💡 Best variants preserved: {sum(len(files) for files in rom_groups.values()) - removed_count}"
            )

        except Exception as e:
            logger.error(f"Error in duplicate detection: {e}")
            self.log_message(f"❌ Error during analysis: {e}")
            to_remove = []
            removed_count = 0

        # Perform the removal operation
        if to_remove:
            self.log_message(f"\n{operation.upper()} OPERATION:")
            self.log_message(f"Files to {operation}: {len(to_remove)}")
            self.log_message(
                f"Moving files to: {self.directory_var.get()}/removed_duplicates"
            )

            if operation == "move":
                self.move_files(to_remove)
            elif operation == "delete":
                self.delete_files(to_remove)
        else:
            self.log_message("\nNo duplicate files found!")

        self.status_var.set(f"Complete - {removed_count} duplicates handled")
        self.progress_var.set(100)

    def move_files(self, files_to_move):
        """Move files to a subdirectory."""
        if not files_to_move:
            return

        # Create subdirectory
        first_file = files_to_move[0]
        base_dir = first_file.parent
        removed_dir = base_dir / "removed_duplicates"
        removed_dir.mkdir(exist_ok=True)

        self.log_message(f"Moving files to: {removed_dir}")

        for i, file_path in enumerate(files_to_move):
            # Check if stop was requested
            if self.process_stop_requested:
                self.log_message("STOP: Process stopped by user request")
                self.status_var.set("Process stopped")
                return

            try:
                dest_path = removed_dir / file_path.name
                # Handle name conflicts
                counter = 1
                while dest_path.exists():
                    stem = file_path.stem
                    suffix = file_path.suffix
                    dest_path = removed_dir / f"{stem}_{counter}{suffix}"
                    counter += 1

                shutil.move(str(file_path), str(dest_path))
                self.log_message(f"  Moved: {file_path.name}")

                # Update progress
                progress = ((i + 1) / len(files_to_move)) * 100
                self.progress_var.set(progress)
                self.root.update_idletasks()

            except Exception as e:
                self.log_message(f"  Error moving {file_path}: {e}")

    def delete_files(self, files_to_delete):
        """Delete files permanently."""
        if not files_to_delete:
            return

        # Confirm deletion
        response = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete {len(files_to_delete)} files?\n\n"
            "This operation cannot be undone!",
        )

        if not response:
            self.log_message("Deletion cancelled by user")
            return

        self.log_message("Permanently deleting files...")

        for i, file_path in enumerate(files_to_delete):
            # Check if stop was requested
            if self.process_stop_requested:
                self.log_message("STOP: Process stopped by user request")
                self.status_var.set("Process stopped")
                return

            try:
                file_path.unlink()
                self.log_message(f"  Deleted: {file_path.name}")

                # Update progress
                progress = ((i + 1) / len(files_to_delete)) * 100
                self.progress_var.set(progress)
                self.root.update_idletasks()

            except Exception as e:
                self.log_message(f"  Error deleting {file_path}: {e}")


def load_game_cache():
    """Load game database cache from file."""
    global GAME_CACHE
    # Auto-delete cache on startup for always fresh results
    if CACHE_FILE.exists():
        try:
            CACHE_FILE.unlink()
            print("Cleared cache for fresh API results")
        except Exception as e:
            print(f"Warning: Could not clear cache: {e}")
    GAME_CACHE = {}  # Reset the global cache dictionary


def save_game_cache():
    """Save game database cache to file."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(GAME_CACHE, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(GAME_CACHE)} entries to game cache")
    except Exception as e:
        print(f"Warning: Could not save cache: {e}")


def load_api_credentials() -> Dict[str, str]:
    """Load API credentials from secure storage.

    Returns:
        Dictionary containing API credentials
    """
    try:
        credential_manager = get_credential_manager()

        # Load credentials from secure storage, with default fallback
        tgdb_api_key = (
            credential_manager.get_credential("tgdb_api_key") or DEFAULT_TGDB_API_KEY
        )
        igdb_client_id = credential_manager.get_credential("igdb_client_id") or ""
        igdb_access_token = credential_manager.get_credential("igdb_access_token") or ""
        api_choice = credential_manager.get_credential("api_choice") or "igdb"

        return {
            "api_choice": api_choice,
            "tgdb_api_key": tgdb_api_key,
            "igdb_client_id": igdb_client_id,
            "igdb_access_token": igdb_access_token,
        }
    except Exception as e:
        logger.error(f"Error loading API credentials: {e}")
        return {
            "api_choice": "igdb",
            "tgdb_api_key": "",
            "igdb_client_id": "",
            "igdb_access_token": "",
        }


def save_api_credentials(
    api_choice: str,
    tgdb_api_key: str = "",
    igdb_client_id: str = "",
    igdb_access_token: str = "",
) -> bool:
    """Save API credentials to secure storage.

    Args:
        api_choice: Selected API ("thegamesdb" or "igdb")
        tgdb_api_key: TheGamesDB API key
        igdb_client_id: IGDB client ID
        igdb_access_token: IGDB access token

    Returns:
        True if credentials saved successfully, False otherwise
    """
    try:
        credential_manager = get_credential_manager()

        # Save all credentials to secure storage
        success = True

        # Save API choice
        if not credential_manager.store_credential("api_choice", api_choice):
            success = False

        # Save TheGamesDB credentials
        if tgdb_api_key.strip():
            if not credential_manager.store_credential(
                "tgdb_api_key", tgdb_api_key.strip()
            ):
                success = False
        else:
            credential_manager.delete_credential("tgdb_api_key")

        # Save IGDB credentials
        if igdb_client_id.strip():
            if not credential_manager.store_credential(
                "igdb_client_id", igdb_client_id.strip()
            ):
                success = False
        else:
            credential_manager.delete_credential("igdb_client_id")

        if igdb_access_token.strip():
            if not credential_manager.store_credential(
                "igdb_access_token", igdb_access_token.strip()
            ):
                success = False
        else:
            credential_manager.delete_credential("igdb_access_token")

        if success:
            logger.info("API credentials saved successfully to secure storage")
        else:
            logger.error("Some credentials could not be saved")

        return success

    except Exception as e:
        logger.error(f"Error saving API credentials: {e}")
        return False


# TheGamesDB query functions are now imported from tgdb_query.py
# This provides query_tgdb_game() and get_canonical_name() functions


def setup_dark_theme(root, style):
    """Set up a beautiful dark theme for the application."""

    # Configure root window
    root.configure(bg="#1e1e1e")

    # Dark color palette
    colors = {
        "bg_primary": "#1e1e1e",  # Main background
        "bg_secondary": "#2d2d2d",  # Secondary background (frames, etc.)
        "bg_tertiary": "#3c3c3c",  # Tertiary background (buttons, entries)
        "bg_accent": "#404040",  # Accent background (hover states)
        "fg_primary": "#ffffff",  # Primary text
        "fg_secondary": "#b0b0b0",  # Secondary text
        "fg_accent": "#64b5f6",  # Accent text (links, highlights)
        "border": "#555555",  # Border color
        "success": "#4caf50",  # Success color (green)
        "warning": "#ff9800",  # Warning color (orange)
        "error": "#f44336",  # Error color (red)
        "info": "#2196f3",  # Info color (blue)
    }

    # Configure ttk styles
    style.theme_use("clam")

    # Configure main frame style
    style.configure("Dark.TFrame", background=colors["bg_primary"], borderwidth=0)

    # Configure secondary frame style
    style.configure(
        "Secondary.TFrame",
        background=colors["bg_secondary"],
        borderwidth=1,
        relief="solid",
    )

    # Configure notebook style
    style.configure("Dark.TNotebook", background=colors["bg_primary"], borderwidth=0)

    style.configure(
        "Dark.TNotebook.Tab",
        background=colors["bg_tertiary"],
        foreground=colors["fg_primary"],
        padding=[20, 8],
        borderwidth=1,
        focuscolor="none",
    )

    style.map(
        "Dark.TNotebook.Tab",
        background=[("selected", colors["bg_accent"]), ("active", colors["bg_accent"])],
        foreground=[
            ("selected", colors["fg_primary"]),
            ("active", colors["fg_primary"]),
        ],
    )

    # Configure label styles
    style.configure(
        "Dark.TLabel",
        background=colors["bg_primary"],
        foreground=colors["fg_primary"],
        font=("Segoe UI", 9),
    )

    style.configure(
        "Heading.TLabel",
        background=colors["bg_primary"],
        foreground=colors["fg_primary"],
        font=("Segoe UI", 11, "bold"),
    )

    style.configure(
        "Subtitle.TLabel",
        background=colors["bg_primary"],
        foreground=colors["fg_accent"],
        font=("Segoe UI", 10, "bold"),
    )

    style.configure(
        "Success.TLabel",
        background=colors["bg_primary"],
        foreground=colors["success"],
        font=("Segoe UI", 9),
    )

    style.configure(
        "Warning.TLabel",
        background=colors["bg_primary"],
        foreground=colors["warning"],
        font=("Segoe UI", 9),
    )

    style.configure(
        "Error.TLabel",
        background=colors["bg_primary"],
        foreground=colors["error"],
        font=("Segoe UI", 9),
    )

    # Configure button styles
    style.configure(
        "Dark.TButton",
        background=colors["bg_tertiary"],
        foreground=colors["fg_primary"],
        borderwidth=1,
        relief="solid",
        padding=[16, 8],
        font=("Segoe UI", 9),
    )

    style.map(
        "Dark.TButton",
        background=[("active", colors["bg_accent"]), ("pressed", colors["border"])],
        foreground=[
            ("active", colors["fg_primary"]),
            ("pressed", colors["fg_primary"]),
        ],
        relief=[("pressed", "solid"), ("!pressed", "solid")],
    )

    # Configure primary button style
    style.configure(
        "Primary.TButton",
        background=colors["fg_accent"],
        foreground="white",
        borderwidth=1,
        relief="solid",
        padding=[16, 8],
        font=("Segoe UI", 9, "bold"),
    )

    style.map(
        "Primary.TButton",
        background=[("active", "#5aa3e8"), ("pressed", "#4a93d8")],
        foreground=[("active", "white"), ("pressed", "white")],
    )

    # Configure entry styles
    style.configure(
        "Dark.TEntry",
        background="white",  # White background for better readability
        foreground="black",  # Black text for maximum contrast
        borderwidth=1,
        relief="solid",
        insertcolor="black",  # Black cursor
        selectbackground=colors["fg_accent"],
        selectforeground="white",
        padding=[8, 6],
        font=("Segoe UI", 9),
    )

    style.map(
        "Dark.TEntry",
        focuscolor=[("focus", colors["fg_accent"])],
        bordercolor=[("focus", colors["fg_accent"])],
    )

    # Configure radiobutton styles
    style.configure(
        "Dark.TRadiobutton",
        background=colors["bg_primary"],
        foreground=colors["fg_primary"],
        focuscolor="none",
        font=("Segoe UI", 9),
    )

    style.map(
        "Dark.TRadiobutton",
        background=[("active", colors["bg_primary"])],
        foreground=[("active", colors["fg_primary"])],
    )

    # Configure checkbutton styles
    style.configure(
        "Dark.TCheckbutton",
        background=colors["bg_primary"],
        foreground=colors["fg_primary"],
        focuscolor="none",
        font=("Segoe UI", 9),
    )

    style.map(
        "Dark.TCheckbutton",
        background=[("active", colors["bg_primary"])],
        foreground=[("active", colors["fg_primary"])],
    )

    # Configure labelframe styles
    style.configure(
        "Dark.TLabelframe",
        background=colors["bg_primary"],
        borderwidth=1,
        relief="solid",
    )

    style.configure(
        "Dark.TLabelframe.Label",
        background=colors["bg_primary"],
        foreground=colors["fg_accent"],
        font=("Segoe UI", 9, "bold"),
    )

    # Configure progressbar styles
    style.configure(
        "Dark.Horizontal.TProgressbar",
        background=colors["fg_accent"],
        troughcolor=colors["bg_tertiary"],
        borderwidth=1,
        lightcolor=colors["fg_accent"],
        darkcolor=colors["fg_accent"],
    )

    # Configure scrollbar styles
    style.configure(
        "Dark.Vertical.TScrollbar",
        background=colors["bg_tertiary"],
        troughcolor=colors["bg_secondary"],
        borderwidth=1,
        arrowcolor=colors["fg_secondary"],
        darkcolor=colors["bg_tertiary"],
        lightcolor=colors["bg_tertiary"],
    )

    style.map(
        "Dark.Vertical.TScrollbar",
        background=[("active", colors["bg_accent"])],
        arrowcolor=[("active", colors["fg_primary"])],
    )


def main():
    """Main application entry point"""
    # Load the game cache on startup
    load_game_cache()

    # Create and run the GUI
    root = tk.Tk()

    # Configure the style
    style = ttk.Style()
    setup_dark_theme(root, style)

    app = ROMCleanupGUI(root)

    def on_closing():
        """Handle application closing."""
        # Save cache before closing
        save_game_cache()

        # Stop any running process
        if app.current_process and app.current_process.is_alive():
            app.process_stop_requested = True
            app.current_process.join(timeout=2)

        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main()
