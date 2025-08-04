#!/usr/bin/env python
"""
ROM Collection Cleanup Tool - GUI Version

A streamlined, user-friendly GUI tool for managing ROM collections
by removing duplicates based on region preferences while preserving
unique releases.
"""

import hashlib
import json
import shutil
import sys
import threading
import time
import tkinter as tk
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, scrolledtext, ttk

from rom_constants import PLATFORM_MAPPING, ROM_EXTENSIONS
from rom_utils import get_base_name, get_region

try:
    import requests
except ImportError:
    requests = None
    print(
        "The 'requests' library is required for IGDB features. "
        "Please install it to enable them."
    )
from difflib import SequenceMatcher

# Try to import pyperclip for clipboard functionality
try:
    import pyperclip

    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False

# IGDB configuration
GAME_CACHE = {}
CACHE_FILE = Path("game_cache.json")


class ConsoleRedirector:
    """Redirect console output to GUI log"""

    def __init__(self, gui_logger):
        self.gui_logger = gui_logger

    def write(self, text):
        if text.strip():  # Only log non-empty messages
            self.gui_logger(f"CONSOLE: {text.strip()}")

    def flush(self):
        pass


class ROMCleanupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ROM Collection Cleanup Tool with IGDB Integration")
        self.root.geometry("1200x950")
        self.root.minsize(900, 700)

        # Configure window properties for modern look
        try:
            # Remove any transparency for solid appearance
            self.root.wm_attributes("-alpha", 1.0)  # Fully opaque
        except Exception:
            pass  # Ignore if not supported on this platform

        # Console redirection setup
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.console_redirector = None

        # Process control
        self.current_process = None
        self.process_stop_requested = False

        # Configuration variables
        self.rom_directory = tk.StringVar()
        self.operation_mode = tk.StringVar(value="move")  # move, delete, backup
        self.region_priority = tk.StringVar(value="usa")
        self.keep_japanese_only = tk.BooleanVar(value=True)
        self.keep_europe_only = tk.BooleanVar(value=True)
        self.custom_extensions = tk.StringVar()
        self.create_backup = tk.BooleanVar(value=False)
        self.preserve_subdirs = tk.BooleanVar(value=True)

        # API credentials
        self.igdb_client_id = tk.StringVar()
        self.igdb_access_token = tk.StringVar()

        # API status tracking
        self.api_status_var = tk.StringVar(value="Not configured")
        self.api_status_color = tk.StringVar(value="#ff6b6b")  # Red for not configured

        # ROM file extensions (comprehensive list)
        self.ROM_EXTENSIONS = set(ROM_EXTENSIONS)

        self.setup_dark_theme()
        self.setup_ui()
        self.setup_console_redirection()

    def setup_dark_theme(self):
        """Configure enhanced dark theme for the GUI"""
        # Modern dark color palette
        self.colors = {
            "bg_primary": "#1a1a1a",  # Main background - deeper black
            "bg_secondary": "#2d2d2d",  # Secondary background - elevated surfaces
            "bg_tertiary": "#3a3a3a",  # Tertiary background - input fields
            "bg_accent": "#0f0f0f",  # Deepest background for log area
            "text_primary": "#ffffff",  # Primary text - white
            "text_secondary": "#b0b0b0",  # Secondary text - dimmed white
            "text_accent": "#64b5f6",  # Accent text - blue
            "accent_primary": "#2196f3",  # Primary accent - modern blue
            "accent_hover": "#42a5f5",  # Hover state
            "accent_pressed": "#1976d2",  # Pressed state
            "success": "#4caf50",  # Success green
            "success_hover": "#66bb6a",  # Success hover
            "success_pressed": "#388e3c",  # Success pressed
            "warning": "#ff9800",  # Warning orange
            "danger": "#f44336",  # Danger red
            "border": "#404040",  # Border color
            "shadow": "#0a0a0a",  # Shadow color
        }

        self.root.configure(bg=self.colors["bg_primary"])

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Enhanced style configurations with modern look
        style_configs = {
            "Dark.TFrame": {
                "background": self.colors["bg_primary"],
                "borderwidth": 0,
                "relief": "flat",
            },
            "Card.TFrame": {
                "background": self.colors["bg_secondary"],
                "borderwidth": 1,
                "relief": "solid",
                "bordercolor": self.colors["border"],
            },
            "Dark.TLabel": {
                "background": self.colors["bg_primary"],
                "foreground": self.colors["text_primary"],
                "font": ("Segoe UI", 10),
            },
            "Secondary.TLabel": {
                "background": self.colors["bg_primary"],
                "foreground": self.colors["text_secondary"],
                "font": ("Segoe UI", 9),
            },
            "Title.TLabel": {
                "background": self.colors["bg_primary"],
                "foreground": self.colors["text_accent"],
                "font": ("Segoe UI", 14, "bold"),
            },
            "Subtitle.TLabel": {
                "background": self.colors["bg_primary"],
                "foreground": self.colors["text_accent"],
                "font": ("Segoe UI", 11, "bold"),
            },
            "Dark.TEntry": {
                "fieldbackground": self.colors["bg_tertiary"],
                "background": self.colors["bg_tertiary"],
                "foreground": self.colors["text_primary"],
                "borderwidth": 2,
                "insertcolor": self.colors["text_primary"],
                "selectbackground": self.colors["accent_primary"],
                "selectforeground": self.colors["text_primary"],
                "relief": "flat",
                "padding": [8, 6],
            },
            "Dark.TButton": {
                "background": self.colors["bg_tertiary"],
                "foreground": self.colors["text_primary"],
                "borderwidth": 0,
                "focuscolor": "none",
                "font": ("Segoe UI", 10),
                "padding": [16, 8],
                "relief": "flat",
            },
            "Accent.TButton": {
                "background": self.colors["accent_primary"],
                "foreground": self.colors["text_primary"],
                "borderwidth": 0,
                "focuscolor": "none",
                "font": ("Segoe UI", 10, "bold"),
                "padding": [20, 10],
                "relief": "flat",
            },
            "Success.TButton": {
                "background": self.colors["success"],
                "foreground": self.colors["text_primary"],
                "borderwidth": 0,
                "focuscolor": "none",
                "font": ("Segoe UI", 10, "bold"),
                "padding": [16, 8],
                "relief": "flat",
            },
            "Dark.TCheckbutton": {
                "background": self.colors["bg_primary"],
                "foreground": self.colors["text_primary"],
                "focuscolor": self.colors["accent_primary"],
                "font": ("Segoe UI", 10),
                "indicatorcolor": self.colors["bg_tertiary"],
                "indicatorrelief": "flat",
            },
            "Dark.TRadiobutton": {
                "background": self.colors["bg_primary"],
                "foreground": self.colors["text_primary"],
                "focuscolor": self.colors["accent_primary"],
                "font": ("Segoe UI", 10),
                "indicatorcolor": self.colors["bg_tertiary"],
                "indicatorrelief": "flat",
            },
            "Dark.TCombobox": {
                "fieldbackground": self.colors["bg_tertiary"],
                "background": self.colors["bg_tertiary"],
                "foreground": self.colors["text_primary"],
                "borderwidth": 2,
                "selectbackground": self.colors["accent_primary"],
                "selectforeground": self.colors["text_primary"],
                "arrowcolor": self.colors["text_secondary"],
                "relief": "flat",
            },
            "Dark.Horizontal.TProgressbar": {
                "background": self.colors["accent_primary"],
                "troughcolor": self.colors["bg_tertiary"],
                "borderwidth": 0,
                "lightcolor": self.colors["accent_primary"],
                "darkcolor": self.colors["accent_primary"],
                "relief": "flat",
            },
            "Dark.TNotebook": {
                "background": self.colors["bg_primary"],
                "borderwidth": 0,
                "tabmargins": [0, 0, 0, 0],
            },
            "Dark.TNotebook.Tab": {
                "background": self.colors["bg_secondary"],
                "foreground": self.colors["text_secondary"],
                "padding": [20, 12],
                "font": ("Segoe UI", 10),
                "borderwidth": 0,
                "relief": "flat",
            },
            "Dark.Vertical.TScrollbar": {
                "background": self.colors["bg_tertiary"],
                "troughcolor": self.colors["bg_secondary"],
                "borderwidth": 0,
                "arrowcolor": self.colors["text_secondary"],
                "relief": "flat",
                "width": 12,
            },
        }

        for style_name, options in style_configs.items():
            self.style.configure(style_name, **options)

        # Enhanced hover and interaction states with better contrast
        style_maps = {
            "Dark.TEntry": {
                "focuscolor": [("focus", self.colors["accent_primary"])],
                "bordercolor": [("focus", self.colors["accent_primary"])],
            },
            "Dark.TButton": {
                "background": [
                    ("active", "#404040"),  # Darker hover for better contrast
                    ("pressed", "#303030"),  # Even darker when pressed
                    ("disabled", self.colors["bg_secondary"]),
                ],
                "foreground": [("disabled", self.colors["text_secondary"])],
            },
            "Accent.TButton": {
                "background": [
                    ("active", self.colors["accent_pressed"]),  # Use darker accent
                    ("pressed", "#1565c0"),  # Even darker pressed state
                    ("disabled", self.colors["bg_secondary"]),
                ],
                "foreground": [("disabled", self.colors["text_secondary"])],
            },
            "Success.TButton": {
                "background": [
                    ("active", self.colors["success_pressed"]),  # Use darker green
                    ("pressed", "#2e7d32"),  # Even darker pressed state
                    ("disabled", self.colors["bg_secondary"]),
                ],
                "foreground": [("disabled", self.colors["text_secondary"])],
            },
            "Dark.TCheckbutton": {
                "indicatorcolor": [
                    ("selected", self.colors["accent_primary"]),
                    (
                        "active",
                        self.colors["accent_primary"],
                    ),  # Keep same color, don't lighten
                ],
                "background": [
                    (
                        "active",
                        self.colors["bg_primary"],
                    )  # Keep background same on hover
                ],
            },
            "Dark.TRadiobutton": {
                "indicatorcolor": [
                    ("selected", self.colors["accent_primary"]),
                    (
                        "active",
                        self.colors["accent_primary"],
                    ),  # Keep same color, don't lighten
                ],
                "background": [
                    (
                        "active",
                        self.colors["bg_primary"],
                    )  # Keep background same on hover
                ],
            },
            "Dark.TNotebook.Tab": {
                "background": [
                    ("selected", self.colors["accent_primary"]),
                    ("active", "#404040"),  # Darker hover for tabs
                ],
                "foreground": [
                    ("selected", self.colors["text_primary"]),
                    ("active", self.colors["text_primary"]),
                ],
            },
            "Dark.Vertical.TScrollbar": {
                "background": [
                    ("active", self.colors["accent_primary"]),
                    ("pressed", self.colors["accent_pressed"]),
                ],
                "arrowcolor": [
                    ("active", self.colors["text_primary"]),
                    ("pressed", self.colors["text_primary"]),
                ],
            },
        }

        for style_name, maps in style_maps.items():
            for option, values in maps.items():
                self.style.map(style_name, **{option: values})

    def setup_ui(self):
        # Create main frame with enhanced padding for modern spacing
        main_frame = ttk.Frame(self.root, padding="20", style="Dark.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Directory selection with modern title
        ttk.Label(main_frame, text="ROM Directory", style="Subtitle.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10)
        )
        dir_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        dir_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(0, weight=1)

        ttk.Entry(
            dir_frame, textvariable=self.rom_directory, width=50, style="Dark.TEntry"
        ).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(
            dir_frame,
            text="Browse",
            command=self.browse_directory,
            style="Dark.TButton",
        ).grid(row=0, column=1)

        # Create notebook for organized options with modern spacing
        notebook = ttk.Notebook(main_frame, style="Dark.TNotebook")
        notebook.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky=(tk.W, tk.E, tk.N, tk.S),
            pady=(10, 20),
        )
        main_frame.rowconfigure(2, weight=1)

        # Basic Options Tab
        basic_frame = ttk.Frame(notebook, padding="20", style="Dark.TFrame")
        notebook.add(basic_frame, text="Basic Options")

        # Operation mode with modern title
        ttk.Label(basic_frame, text="Operation Mode", style="Subtitle.TLabel").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10)
        )
        mode_frame = ttk.Frame(basic_frame, style="Dark.TFrame")
        mode_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Radiobutton(
            mode_frame,
            text="Move to 'to_delete' folder (Safest)",
            variable=self.operation_mode,
            value="move",
            style="Dark.TRadiobutton",
        ).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(
            mode_frame,
            text="Delete immediately",
            variable=self.operation_mode,
            value="delete",
            style="Dark.TRadiobutton",
        ).grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(
            mode_frame,
            text="Copy to backup folder first",
            variable=self.operation_mode,
            value="backup",
            style="Dark.TRadiobutton",
        ).grid(row=2, column=0, sticky=tk.W)

        # Region priority
        ttk.Label(basic_frame, text="Preferred Region", style="Subtitle.TLabel").grid(
            row=2, column=0, sticky=tk.W, pady=(20, 10)
        )
        region_frame = ttk.Frame(basic_frame, style="Dark.TFrame")
        region_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))

        ttk.Radiobutton(
            region_frame,
            text="USA",
            variable=self.region_priority,
            value="usa",
            style="Dark.TRadiobutton",
        ).grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(
            region_frame,
            text="Europe",
            variable=self.region_priority,
            value="europe",
            style="Dark.TRadiobutton",
        ).grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        ttk.Radiobutton(
            region_frame,
            text="Japan",
            variable=self.region_priority,
            value="japan",
            style="Dark.TRadiobutton",
        ).grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        ttk.Radiobutton(
            region_frame,
            text="World",
            variable=self.region_priority,
            value="world",
            style="Dark.TRadiobutton",
        ).grid(row=0, column=3, sticky=tk.W, padx=(20, 0))

        # Preservation options
        ttk.Label(
            basic_frame, text="Preservation Options", style="Subtitle.TLabel"
        ).grid(row=4, column=0, sticky=tk.W, pady=(20, 10))
        ttk.Checkbutton(
            basic_frame,
            text="Keep Japanese-only releases",
            variable=self.keep_japanese_only,
            style="Dark.TCheckbutton",
        ).grid(row=5, column=0, sticky=tk.W)
        ttk.Checkbutton(
            basic_frame,
            text="Keep Europe-only releases",
            variable=self.keep_europe_only,
            style="Dark.TCheckbutton",
        ).grid(row=6, column=0, sticky=tk.W)
        ttk.Checkbutton(
            basic_frame,
            text="Preserve subdirectory structure",
            variable=self.preserve_subdirs,
            style="Dark.TCheckbutton",
        ).grid(row=7, column=0, sticky=tk.W)

        # Advanced Options Tab with scrolling
        advanced_tab_frame = ttk.Frame(notebook, style="Dark.TFrame")
        notebook.add(advanced_tab_frame, text="IGDB API")

        # Create canvas and scrollbar for scrollable content
        canvas = tk.Canvas(
            advanced_tab_frame,
            bg=self.colors["bg_primary"],
            highlightthickness=0,
            borderwidth=0,
        )
        scrollbar = ttk.Scrollbar(
            advanced_tab_frame,
            orient="vertical",
            command=canvas.yview,
            style="Dark.Vertical.TScrollbar",
        )
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create the actual content frame inside the canvas
        advanced_frame = ttk.Frame(canvas, padding="20", style="Dark.TFrame")

        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Add the content frame to the canvas
        canvas_frame_id = canvas.create_window(
            (0, 0), window=advanced_frame, anchor="nw"
        )

        # Configure scrolling behavior
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # Update the width of the frame to match canvas width
            canvas_width = canvas.winfo_width()
            if canvas_width > 1:
                canvas.itemconfig(canvas_frame_id, width=canvas_width)

        advanced_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Configure>", configure_scroll_region)

        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        # Bind mousewheel to canvas and all child widgets
        def bind_mousewheel(widget):
            widget.bind("<MouseWheel>", on_mousewheel)
            for child in widget.winfo_children():
                bind_mousewheel(child)

        bind_mousewheel(advanced_tab_frame)

        # IGDB API Configuration
        ttk.Label(
            advanced_frame, text="IGDB API Configuration", style="Subtitle.TLabel"
        ).grid(row=0, column=0, sticky=tk.W, pady=(0, 15))

        ttk.Label(advanced_frame, text="Client ID:", style="Dark.TLabel").grid(
            row=1, column=0, sticky=tk.W, pady=(0, 5)
        )
        ttk.Entry(
            advanced_frame,
            textvariable=self.igdb_client_id,
            width=50,
            style="Dark.TEntry",
        ).grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        ttk.Label(advanced_frame, text="Access Token:", style="Dark.TLabel").grid(
            row=3, column=0, sticky=tk.W, pady=(0, 5)
        )
        ttk.Entry(
            advanced_frame,
            textvariable=self.igdb_access_token,
            width=50,
            style="Dark.TEntry",
            show="*",
        ).grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))

        # API Status indicator
        ttk.Label(advanced_frame, text="API Status:", style="Dark.TLabel").grid(
            row=5, column=0, sticky=tk.W, pady=(5, 0)
        )
        self.api_status_label = ttk.Label(
            advanced_frame, textvariable=self.api_status_var, style="Dark.TLabel"
        )
        self.api_status_label.grid(row=6, column=0, sticky=tk.W, pady=(0, 10))

        # Bind validation to credential changes
        self.igdb_client_id.trace("w", lambda *args: self.validate_api_credentials())
        self.igdb_access_token.trace("w", lambda *args: self.validate_api_credentials())

        # Add a button to show detailed API error info
        ttk.Button(
            advanced_frame,
            text="Test API Connection",
            command=self.show_api_details,
            style="Dark.TButton",
        ).grid(row=6, column=1, sticky=tk.W, pady=(0, 10), padx=(10, 0))

        ttk.Label(
            advanced_frame,
            text="Get your IGDB API credentials from: https://api.igdb.com/",
            style="Secondary.TLabel",
        ).grid(row=7, column=0, sticky=tk.W, pady=(0, 20))

        # Custom File Extensions
        ttk.Label(
            advanced_frame, text="Custom File Extensions:", style="Dark.TLabel"
        ).grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(
            advanced_frame,
            textvariable=self.custom_extensions,
            width=40,
            style="Dark.TEntry",
        ).grid(row=9, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(
            advanced_frame,
            text="(comma-separated, e.g. .rom,.img)",
            style="Secondary.TLabel",
        ).grid(row=10, column=0, sticky=tk.W, pady=(0, 15))

        ttk.Checkbutton(
            advanced_frame,
            text="Create backup before any operations",
            variable=self.create_backup,
            style="Dark.TCheckbutton",
        ).grid(row=11, column=0, sticky=tk.W, pady=(0, 10))

        # Current extensions display
        ttk.Label(
            advanced_frame, text="Supported Extensions:", style="Dark.TLabel"
        ).grid(row=12, column=0, sticky=tk.W, pady=(10, 5))
        ext_text = scrolledtext.ScrolledText(
            advanced_frame,
            height=6,
            width=50,
            bg=self.colors["bg_tertiary"],
            fg=self.colors["text_primary"],
            insertbackground=self.colors["text_primary"],
            selectbackground=self.colors["accent_primary"],
            selectforeground=self.colors["text_primary"],
            font=("Consolas", 10),
            relief="flat",
            borderwidth=0,
        )
        ext_text.grid(row=13, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ext_text.insert(tk.END, ", ".join(sorted(self.ROM_EXTENSIONS)))
        ext_text.config(state=tk.DISABLED)
        advanced_frame.columnconfigure(0, weight=1)

        # Action buttons
        button_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))

        # Main action buttons
        main_buttons_frame = ttk.Frame(button_frame, style="Dark.TFrame")
        main_buttons_frame.pack(side=tk.LEFT, padx=(0, 20))

        ttk.Button(
            main_buttons_frame,
            text="Scan ROMs",
            command=self.scan_roms,
            style="Accent.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            main_buttons_frame,
            text="Preview Changes",
            command=self.preview_changes_button,
            style="Dark.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            main_buttons_frame,
            text="Execute",
            command=self.execute_operation,
            style="Success.TButton",
        ).pack(side=tk.LEFT)

        # Control buttons
        control_buttons_frame = ttk.Frame(button_frame, style="Dark.TFrame")
        control_buttons_frame.pack(side=tk.RIGHT)

        ttk.Button(
            control_buttons_frame,
            text="Check API",
            command=self.force_api_check,
            style="Dark.TButton",
        ).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(
            control_buttons_frame,
            text="Stop Process",
            command=self.stop_process,
            style="Dark.TButton",
        ).pack(side=tk.LEFT)

        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame,
            variable=self.progress_var,
            maximum=100,
            style="Dark.Horizontal.TProgressbar",
        )
        self.progress_bar.grid(
            row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5)
        )

        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var, style="Dark.TLabel").grid(
            row=5, column=0, columnspan=3, pady=(0, 5)
        )

        # Results/Log area
        ttk.Label(main_frame, text="Results:", style="Dark.TLabel").grid(
            row=6, column=0, sticky=tk.W, pady=(10, 5)
        )

        # Create a frame for the log area with better resizing
        log_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        log_frame.grid(
            row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0)
        )
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=20,
            width=100,
            bg=self.colors["bg_accent"],
            fg=self.colors["text_primary"],
            insertbackground=self.colors["text_primary"],
            selectbackground=self.colors["accent_primary"],
            selectforeground=self.colors["text_primary"],
            font=("Consolas", 10),
            wrap=tk.WORD,
            relief="flat",
            borderwidth=0,
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Add action buttons for the log
        log_button_frame = ttk.Frame(log_frame, style="Dark.TFrame")
        log_button_frame.grid(row=0, column=1, sticky=(tk.N, tk.E), padx=(5, 0))

        if CLIPBOARD_AVAILABLE:
            ttk.Button(
                log_button_frame,
                text="Copy to Clipboard",
                command=self.copy_log_to_clipboard,
                style="Dark.TButton",
            ).grid(row=0, column=0, pady=(0, 5))

        ttk.Button(
            log_button_frame,
            text="Clear Log",
            command=self.clear_log,
            style="Dark.TButton",
        ).grid(row=1, column=0)

        main_frame.rowconfigure(7, weight=1)

    def setup_console_redirection(self):
        """Set up console output redirection to GUI"""
        self.console_redirector = ConsoleRedirector(self.log_message)
        sys.stdout = self.console_redirector
        sys.stderr = self.console_redirector

    def restore_console(self):
        """Restore original console output"""
        if self.console_redirector:
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr

    def browse_directory(self):
        """Browse for ROM directory"""
        directory = filedialog.askdirectory(title="Select ROM Directory")
        if directory:
            self.rom_directory.set(directory)
            self.log_message(f"SUCCESS: Directory selected: {directory}")
            self.status_var.set(f"Directory selected: {Path(directory).name}")

    def copy_log_to_clipboard(self):
        """Copy log contents to clipboard"""
        try:
            log_content = self.log_text.get(1.0, tk.END)
            if CLIPBOARD_AVAILABLE:
                pyperclip.copy(log_content)
                self.log_message("SUCCESS: Log copied to clipboard")
            else:
                # Fallback: copy to system clipboard using tkinter
                self.root.clipboard_clear()
                self.root.clipboard_append(log_content)
                self.root.update()
                self.log_message(
                    "SUCCESS: Log copied to clipboard (using system method)"
                )
        except Exception as e:
            self.log_message(f"ERROR: Failed to copy to clipboard: {e}")
            messagebox.showerror(
                "Clipboard Error", f"Failed to copy log to clipboard:\n{e}"
            )

    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()

    def clear_log(self):
        """Clear the log text area"""
        self.log_text.delete(1.0, tk.END)
        self.log_message("INFO: Log cleared")

    def check_api_connection(self):
        """Check IGDB API connection and return status"""
        client_id = self.igdb_client_id.get().strip()
        access_token = self.igdb_access_token.get().strip()

        if not client_id:
            return (
                False,
                "IGDB Client ID not configured - "
                "enter your credentials in IGDB API tab",
            )
        elif not access_token:
            return (
                False,
                "IGDB Access Token not configured - "
                "enter your credentials in IGDB API tab",
            )
        elif not requests:
            return False, "requests library not available"

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
                return True, "API connection successful"
            elif response.status_code == 401:
                # Try to get more detailed error information
                try:
                    error_detail = response.text
                    if error_detail:
                        return False, f"Authentication failed (401): {error_detail}"
                    else:
                        return (
                            False,
                            "Authentication failed (401) - check Client ID "
                            "and Access Token",
                        )
                except Exception:
                    return (
                        False,
                        "Authentication failed (401) - check Client ID "
                        "and Access Token",
                    )
            elif response.status_code == 429:
                return False, "Rate limit exceeded (429) - wait a few minutes"
            else:
                return False, f"API test failed - response code: {response.status_code}"

        except requests.exceptions.ConnectionError as e:
            return False, f"Connection error: {e}"
        except requests.exceptions.Timeout as e:
            return False, f"Request timeout: {e}"
        except Exception as e:
            return False, f"API connection error: {e}"

    def validate_api_credentials(self):
        """Validate API credentials and update status"""
        client_id = self.igdb_client_id.get().strip()
        access_token = self.igdb_access_token.get().strip()

        if not client_id or not access_token:
            self.api_status_var.set("Not configured")
            self.api_status_color.set("#ff6b6b")  # Red
            return

        # Test the connection
        success, message = self.check_api_connection()

        if success:
            self.api_status_var.set("Connected")
            self.api_status_color.set("#51cf66")  # Green
        else:
            # Show the specific error message
            error_text = f"{message}"
            if len(error_text) > 50:  # Truncate long error messages
                error_text = error_text[:47] + "..."
            self.api_status_var.set(error_text)
            self.api_status_color.set("#ff6b6b")  # Red

        # Update the status label if it exists
        if hasattr(self, "api_status_label"):
            self.api_status_label.config(
                text=self.api_status_var.get(), foreground=self.api_status_color.get()
            )

    def force_api_check(self):
        """Force API connection check"""
        self.log_message("\n" + "=" * 50)
        self.log_message("FORCING API CONNECTION CHECK")
        self.log_message("=" * 50)

        success, message = self.check_api_connection()

        if success:
            self.log_message(f"SUCCESS: {message}")
            self.log_message("Enhanced game matching is available")
        else:
            self.log_message(f"ERROR: {message}")
            self.log_message("Enhanced game matching is disabled")

        self.log_message("=" * 50)

    def show_api_details(self):
        """Show detailed API connection information"""
        client_id = self.igdb_client_id.get().strip()
        access_token = self.igdb_access_token.get().strip()

        self.log_message("\n" + "=" * 50)
        self.log_message("DETAILED API CONNECTION INFO")
        self.log_message("=" * 50)

        # Show credential status (masked)
        if client_id:
            masked_client_id = (
                client_id[:4] + "*" * (len(client_id) - 8) + client_id[-4:]
                if len(client_id) > 8
                else "****"
            )
            self.log_message(f"Client ID: {masked_client_id}")
        else:
            self.log_message("Client ID: NOT SET")

        if access_token:
            masked_token = (
                access_token[:4] + "*" * (len(access_token) - 8) + access_token[-4:]
                if len(access_token) > 8
                else "****"
            )
            self.log_message(f"Access Token: {masked_token}")
        else:
            self.log_message("Access Token: NOT SET")

        # Test connection and show detailed results
        if not client_id or not access_token:
            self.log_message("ERROR: Missing credentials")
            return

        if not requests:
            self.log_message("ERROR: requests library not available")
            return

        try:
            headers = {
                "Client-ID": client_id,
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            }

            self.log_message("Testing connection to IGDB API...")
            response = requests.post(
                "https://api.igdb.com/v4/games",
                headers=headers,
                data="fields name; limit 1;",
                timeout=10,
            )

            self.log_message(f"Response Status Code: {response.status_code}")

            if response.status_code == 200:
                self.log_message("SUCCESS: API connection successful!")
                self.log_message("Your credentials are working correctly.")
            elif response.status_code == 401:
                self.log_message("ERROR: Authentication failed (401)")
                self.log_message("This usually means:")
                self.log_message("  - Client ID is incorrect")
                self.log_message("  - Access Token is incorrect or expired")
                self.log_message("  - You need to regenerate your Access Token")
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
            self.status_var.set("Stopping...")
        else:
            self.log_message("INFO: No active process to stop")

    def scan_roms(self):
        """Scan ROM directory for duplicates with IGDB integration"""
        if not self.rom_directory.get():
            messagebox.showerror("Error", "Please select a ROM directory first.")
            return

        def scan_thread():
            self.status_var.set("Scanning ROMs...")
            self.progress_var.set(0)
            self.process_stop_requested = False
            self.log_text.delete(1.0, tk.END)

            self.log_message("\n" + "=" * 50)
            self.log_message("STARTING ROM SCAN WITH IGDB INTEGRATION")
            self.log_message("=" * 50)
            self.log_message(f"Scanning directory: {self.rom_directory.get()}")

            # Show current settings
            self.log_message(f"Operation mode: {self.operation_mode.get()}")
            self.log_message(f"Preferred region: {self.region_priority.get()}")
            self.log_message(f"Keep Japanese-only: {self.keep_japanese_only.get()}")
            self.log_message(f"Keep Europe-only: {self.keep_europe_only.get()}")
            self.log_message(f"Preserve subdirectories: {self.preserve_subdirs.get()}")
            if self.custom_extensions.get():
                self.log_message(f"Custom extensions: {self.custom_extensions.get()}")
            self.log_message("-" * 50)

            # Test API connectivity
            self.log_message("Testing IGDB API connectivity...")
            success, message = self.check_api_connection()
            if success:
                self.log_message(f"SUCCESS: {message}")
                self.log_message("Enhanced game matching is available")
            else:
                self.log_message(f"ERROR: {message}")
                self.log_message("Enhanced game matching is disabled")

            self.log_message("-" * 50)

            try:
                # Initialize IGDB cache (clears old cache for fresh results)
                self.log_message("Initializing IGDB cache...")
                load_game_cache()

                # Get extensions
                extensions = self.ROM_EXTENSIONS.copy()
                if self.custom_extensions.get():
                    custom_exts = {
                        ext.strip().lower()
                        for ext in self.custom_extensions.get().split(",")
                    }
                    extensions.update(custom_exts)

                # Scan directory
                self.log_message("Scanning directory structure...")
                directory = Path(self.rom_directory.get())
                all_files = list(directory.rglob("*"))
                self.log_message(f"Found {len(all_files)} total files")

                rom_files = [
                    f
                    for f in all_files
                    if f.is_file() and f.suffix.lower() in extensions
                ]
                self.log_message(f"Found {len(rom_files)} ROM files")

                if not rom_files:
                    self.log_message(
                        "ERROR: No ROM files found in the selected directory."
                    )
                    self.status_var.set("No ROM files found")
                    return

                # Group ROMs by canonical name (using IGDB if available)
                rom_groups = defaultdict(list)
                total_files = len(rom_files)
                self.progress_var.set(0)

                self.log_message(f"Processing {total_files} ROM files...")
                self.log_message("Analyzing each file for regional variants...")

                for i, file_path in enumerate(rom_files):
                    # Check if stop was requested
                    if self.process_stop_requested:
                        self.log_message("STOP: Process stopped by user request")
                        self.status_var.set("Process stopped")
                        return

                    if file_path.is_file() and file_path.suffix.lower() in extensions:
                        filename = file_path.name
                        base_name = get_base_name(filename)
                        file_extension = file_path.suffix.lower()
                        region = get_region(filename)

                        # Log every 10th file or first/last files to avoid spam
                        if i == 0 or i == total_files - 1 or (i + 1) % 10 == 0:
                            self.log_message(
                                f"[{i+1}/{total_files}] Processing: {filename}"
                            )
                            self.log_message(f"   Base name: {base_name}")
                            self.log_message(f"   Region: {region}")

                        # Get user credentials for API calls
                        client_id = self.igdb_client_id.get().strip()
                        access_token = self.igdb_access_token.get().strip()

                        canonical_name = get_canonical_name(
                            base_name, file_extension, client_id, access_token
                        )
                        rom_groups[canonical_name].append(
                            (file_path, region, base_name)
                        )

                    # Update progress
                    progress = ((i + 1) / total_files) * 100
                    self.progress_var.set(progress)
                    self.root.update_idletasks()

                self.log_message(f"Found {len(rom_groups)} unique games")

                # Store rom_groups for later use
                self.rom_groups = rom_groups

                # Find duplicates to remove
                to_remove = self.find_duplicates_to_remove(rom_groups)

                if to_remove:
                    self.log_message(f"\nFound {len(to_remove)} files to remove:")
                    for file_path in to_remove:
                        self.log_message(f"  - {file_path.name}")

                    # Show preview
                    try:
                        self.preview_changes(to_remove)
                    except Exception as e:
                        self.log_message(f"ERROR calling preview_changes: {e}")
                        self.status_var.set("Preview failed")
                else:
                    self.log_message(
                        "\nSUCCESS: No duplicates found! "
                        "Your collection is already clean."
                    )
                    self.status_var.set("No duplicates found")

            except Exception as e:
                self.log_message(f"ERROR during scan: {e}")
                self.status_var.set("Scan failed")

        # Run scan in separate thread
        self.current_process = threading.Thread(target=scan_thread)
        self.current_process.start()

    def preview_changes(self, to_remove=None):
        """Show preview of changes that will be made"""
        if to_remove is None:
            if hasattr(self, "rom_groups"):
                to_remove = self.find_duplicates_to_remove(self.rom_groups)
            else:
                self.log_message(
                    "ERROR: No scan data available - please scan ROMs first"
                )
                return

        if not to_remove:
            self.log_message(
                "SUCCESS: No duplicates found to remove with current settings"
            )
            return

        self.log_message("\nPREVIEW - Files to be moved to 'to_delete' folder:")
        self.log_message("=" * 60)

        # Group by game for better readability
        games_preview = defaultdict(list)
        for file_path in to_remove:
            base_name = get_base_name(file_path.name)
            games_preview[base_name].append(file_path)

        for game_name, files in games_preview.items():
            self.log_message(f"\nGAME: {game_name}:")
            for file_path in files:
                region = get_region(file_path.name)
                self.log_message(f"   REMOVE: {file_path.name} [{region}]")

        self.log_message(f"\nTOTAL: Total: {len(to_remove)} files will be moved")
        self.log_message(
            "   WARNING: Files will be moved to 'to_delete' folder (safe operation)"
        )

    def preview_changes_button(self):
        """Button handler for preview changes"""
        try:
            if not hasattr(self, "rom_groups"):
                messagebox.showwarning("No Data", "Please scan for duplicates first.")
                return

            self.preview_changes()
        except Exception as e:
            self.log_message(f"ERROR: Preview error: {e}")
            messagebox.showerror("Error", f"Preview failed: {e}")

    def find_duplicates_to_remove(self, rom_groups):
        """Find which files should be removed based on region preferences"""
        try:
            to_remove = []
            preferred_region = self.region_priority.get()

            # Define priority order based on preference
            priority_orders = {
                "usa": ["usa", "world", "europe", "japan", "unknown"],
                "europe": ["europe", "world", "usa", "japan", "unknown"],
                "japan": ["japan", "world", "usa", "europe", "unknown"],
                "world": ["world", "usa", "europe", "japan", "unknown"],
            }

            priority_order = priority_orders.get(
                preferred_region, priority_orders["usa"]
            )

            for game_name, roms in rom_groups.items():
                if len(roms) <= 1:
                    continue  # No duplicates for this game

                # Sort ROMs by priority (best first)
                sorted_roms = []
                for file_path, region, filename in roms:
                    try:
                        priority = priority_order.index(region)
                    except ValueError:
                        priority = len(priority_order)  # Unknown regions last

                    sorted_roms.append((priority, file_path, region, filename))

                sorted_roms.sort(
                    key=lambda x: x[0]
                )  # Sort by priority (lower = better)

                # The first ROM is the one to keep
                keep_rom = sorted_roms[0]
                self.log_message(
                    f"GAME: {game_name}: Keeping {keep_rom[1].name} [{keep_rom[2]}]"
                )

                # Mark the rest for removal, but check preservation rules
                for priority, file_path, region, filename in sorted_roms[1:]:
                    should_keep = False

                    # Check preservation rules
                    if region == "japan" and self.keep_japanese_only.get():
                        # Count Japanese versions in this group
                        japanese_count = sum(
                            1 for _, _, r, _ in sorted_roms if r == "japan"
                        )
                        if japanese_count == 1:  # This is the only Japanese version
                            should_keep = True
                            self.log_message(
                                f"   PRESERVE: Preserving only Japanese version: "
                                f"{filename}"
                            )

                    elif region == "europe" and self.keep_europe_only.get():
                        # Count European versions in this group
                        european_count = sum(
                            1 for _, _, r, _ in sorted_roms if r == "europe"
                        )
                        if european_count == 1:  # This is the only European version
                            should_keep = True
                            self.log_message(
                                f"   PRESERVE: Preserving only European version: "
                                f"{filename}"
                            )

                    if not should_keep:
                        to_remove.append(file_path)
                        self.log_message(
                            f"   REMOVE: Marking for removal: {filename} [{region}]"
                        )

            return to_remove

        except Exception as e:
            self.log_message(f"ERROR: Error finding duplicates: {e}")
            return []

    def execute_operation(self):
        """Execute the selected operation on found duplicates"""
        if not hasattr(self, "rom_groups"):
            messagebox.showerror(
                "Error", "No files to process. Please scan ROMs first."
            )
            return

        to_remove = self.find_duplicates_to_remove(self.rom_groups)

        if not to_remove:
            messagebox.showinfo(
                "Info", "No duplicates found to remove based on current settings."
            )
            return

        operation = self.operation_mode.get()

        # Confirm before executing with operation-specific message
        if operation == "move":
            message = (
                f"Move {len(to_remove)} duplicate files to 'to_delete' folder?\n\n"
                "This is a safe operation - files will not be permanently deleted."
            )
        elif operation == "backup":
            message = (
                f"Backup and then delete {len(to_remove)} duplicate files?\n\n"
                "Files will be copied to backup folder first, then deleted."
            )
        else:  # delete
            message = (
                f"PERMANENTLY DELETE {len(to_remove)} duplicate files?\n\n"
                "WARNING: This cannot be undone!"
            )

        response = messagebox.askyesno("Confirm Operation", message)

        if not response:
            self.log_message("CANCELLED: Operation cancelled by user")
            return

        def execute_thread():
            self.status_var.set("Executing operation...")
            self.progress_var.set(0)

            self.log_message(
                f"\nExecuting {operation} operation on {len(to_remove)} files..."
            )

            try:
                if operation == "move":
                    self.move_to_safe_folder(to_remove)
                elif operation == "backup":
                    self.backup_and_delete(to_remove)
                else:  # delete
                    self.delete_files(to_remove)

                self.log_message("SUCCESS: Operation completed successfully!")
                self.status_var.set("Operation completed")

            except Exception as e:
                self.log_message(f"ERROR: Error during operation: {e}")
                self.status_var.set("Operation failed")

        # Run in separate thread
        self.current_process = threading.Thread(target=execute_thread)
        self.current_process.start()

    def move_to_safe_folder(self, to_remove):
        """Move files to a safe 'to_delete' folder"""
        # Create safe folder
        safe_folder = Path(self.rom_directory.get()) / "to_delete"
        safe_folder.mkdir(exist_ok=True)

        self.log_message(f"FOLDER: Created safe folder: {safe_folder}")

        for i, file_path in enumerate(to_remove):
            # Check if stop was requested
            if self.process_stop_requested:
                self.log_message("STOP: Process stopped by user request")
                return

            try:
                # Determine destination path
                if self.preserve_subdirs.get():
                    # Preserve directory structure
                    rel_path = file_path.relative_to(Path(self.rom_directory.get()))
                    dest_path = safe_folder / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    # Flat structure in to_delete folder
                    dest_path = safe_folder / file_path.name

                    # Handle filename conflicts
                    counter = 1
                    while dest_path.exists():
                        stem = file_path.stem
                        suffix = file_path.suffix
                        dest_path = safe_folder / f"{stem}_{counter}{suffix}"
                        counter += 1

                # Move the file
                shutil.move(str(file_path), str(dest_path))
                self.log_message(f"   MOVED: Moved: {file_path.name} → to_delete/")

                # Update progress
                progress = ((i + 1) / len(to_remove)) * 100
                self.progress_var.set(progress)
                self.root.update_idletasks()

            except Exception as e:
                self.log_message(f"   ERROR: Error moving {file_path.name}: {e}")

        self.log_message(f"\nSUCCESS: All files moved to: {safe_folder}")
        self.log_message(
            "NOTE: You can review and manually delete these files when ready"
        )

    def backup_and_delete(self, to_remove):
        """Backup files before deleting"""
        self.log_message(f"\nBacking up {len(to_remove)} files before deletion...")

        # Create backup folder
        backup_folder = (
            Path(self.rom_directory.get())
            / "backup"
            / datetime.now().strftime("%Y%m%d_%H%M%S")
        )
        backup_folder.mkdir(parents=True, exist_ok=True)

        # First backup
        for i, file_path in enumerate(to_remove):
            # Check if stop was requested
            if self.process_stop_requested:
                self.log_message("STOP: Process stopped by user request")
                self.status_var.set("Process stopped")
                return

            try:
                # Determine destination path
                if self.preserve_subdirs.get():
                    rel_path = file_path.relative_to(Path(self.rom_directory.get()))
                    dest_path = backup_folder / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    dest_path = backup_folder / file_path.name

                shutil.copy2(str(file_path), str(dest_path))

                # Update progress (backup is 50% of total)
                progress = ((i + 1) / len(to_remove)) * 50
                self.progress_var.set(progress)
                self.root.update_idletasks()

            except Exception as e:
                self.log_message(f"  Error backing up {file_path}: {e}")

        self.log_message(f"Backup completed in: {backup_folder}")
        self.log_message("Now deleting original files...")

        # Then delete
        for i, file_path in enumerate(to_remove):
            # Check if stop was requested
            if self.process_stop_requested:
                self.log_message("STOP: Process stopped by user request")
                self.status_var.set("Process stopped")
                return

            try:
                file_path.unlink()
                self.log_message(f"  Deleted: {file_path.name}")

                # Update progress (deletion is remaining 50%)
                progress = 50 + ((i + 1) / len(to_remove)) * 50
                self.progress_var.set(progress)
                self.root.update_idletasks()

            except Exception as e:
                self.log_message(f"  Error deleting {file_path}: {e}")

    def delete_files(self, to_remove):
        """Delete files immediately"""
        self.log_message(f"\nDeleting {len(to_remove)} files...")

        for i, file_path in enumerate(to_remove):
            # Check if stop was requested
            if self.process_stop_requested:
                self.log_message("STOP: Process stopped by user request")
                self.status_var.set("Process stopped")
                return

            try:
                file_path.unlink()
                self.log_message(f"  Deleted: {file_path.name}")

                # Update progress
                progress = ((i + 1) / len(to_remove)) * 100
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


def query_igdb_game(game_name, file_extension=None, client_id=None, access_token=None):
    """Query IGDB for game information and alternative names."""
    if not requests:
        print("ERROR: requests library not available - IGDB integration disabled")
        return None

    if not client_id:
        print("ERROR: IGDB_CLIENT_ID not provided - API integration disabled")
        return None

    if not access_token:
        print("ERROR: IGDB_ACCESS_TOKEN not provided - API integration disabled")
        return None

    cache_key = hashlib.md5(
        f"{game_name}_{file_extension or 'unknown'}".encode()
    ).hexdigest()

    if cache_key in GAME_CACHE:
        print(f"Cache hit for: {game_name}")
        return GAME_CACHE[cache_key]

    platform_filter = ""
    target_platforms = []
    if file_extension and file_extension.lower() in PLATFORM_MAPPING:
        target_platforms = PLATFORM_MAPPING[file_extension.lower()]
        platform_filter = f"where platforms = ({','.join(map(str, target_platforms))});"

    query = f"""
    search "{game_name}";
    fields name, alternative_names.name, platforms;
    {platform_filter}
    limit 20;
    """

    headers = {
        "Client-ID": client_id,
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "text/plain",
    }

    backoff = 0.5
    for attempt in range(3):
        try:
            response = requests.post(
                "https://api.igdb.com/v4/games",
                headers=headers,
                data=query.strip(),
                timeout=10,
            )

            if response.status_code == 429:
                time.sleep(backoff * (attempt + 1))
                continue

            response.raise_for_status()
            games = response.json()
            print(f"IGDB API returned {len(games)} results for: {game_name}")

            scored_matches = []

            for game in games:
                all_names = [game["name"]]
                if "alternative_names" in game:
                    all_names.extend([alt["name"] for alt in game["alternative_names"]])

                platform_bonus = 0
                if target_platforms and "platforms" in game:
                    game_platforms = [p for p in game["platforms"]]
                    if any(p in target_platforms for p in game_platforms):
                        platform_bonus = 0.2

                # Check all names for matches with improved logic
                best_match_score = 0
                best_match_name = None
                match_type = None

                for name in all_names:
                    ratio = SequenceMatcher(
                        None, game_name.lower(), name.lower()
                    ).ratio()

                    # More lenient thresholds for cross-language matching
                    if name == game["name"]:  # Main name
                        threshold = 0.7  # Lowered from 0.8
                        if ratio >= threshold:
                            final_score = ratio + platform_bonus
                            if final_score > best_match_score:
                                best_match_score = final_score
                                best_match_name = name
                                match_type = "main"
                    else:  # Alternative name - even more lenient
                        threshold = 0.25  # Lowered from 0.3 for cross-language matches
                        if ratio >= threshold:
                            final_score = ratio + platform_bonus
                            if final_score > best_match_score:
                                best_match_score = final_score
                                best_match_name = name
                                match_type = "alternative"

                if best_match_score > 0:
                    scored_matches.append(
                        {
                            "game": game,
                            "score": best_match_score,
                            "match_name": best_match_name,
                            "match_type": match_type,
                            "all_names": all_names,
                        }
                    )

            # Sort by score (highest first)
            scored_matches.sort(key=lambda x: x["score"], reverse=True)

            # Return best match
            if scored_matches:
                best_match = scored_matches[0]
                result = {
                    "canonical_name": best_match["game"]["name"],
                    "alternative_names": best_match["all_names"],
                    "id": best_match["game"]["id"],
                    "match_score": best_match["score"],
                    "matched_on": best_match["match_name"],
                }
                print(
                    f"Best match for '{game_name}': "
                    f"'{best_match['match_name']}' "
                    f"(score: {best_match['score']:.2f})"
                )
                GAME_CACHE[cache_key] = result
                time.sleep(0.25)  # Rate limiting
                return result

            break
        except requests.HTTPError as http_err:
            print(f"IGDB API HTTP error for '{game_name}': {http_err}")
            break
        except Exception as e:
            print(f"IGDB API error for '{game_name}': {e}")
            break
        finally:
            # Rate limiting
            time.sleep(0.25)  # IGDB allows 4 requests per second

    GAME_CACHE[cache_key] = None
    return None


def get_canonical_name(
    game_name, file_extension=None, client_id=None, access_token=None
):
    """Get canonical name using IGDB or fallback to cache/simple matching."""
    print(f"Looking up canonical name for: {game_name} ({file_extension})")

    # Try IGDB first
    igdb_result = query_igdb_game(game_name, file_extension, client_id, access_token)
    if igdb_result:
        # Use the actual matched name, not the canonical IGDB name
        canonical = igdb_result["matched_on"]  # This is the name that actually matched
        if canonical != game_name:
            print(f"Canonical name: '{game_name}' -> '{canonical}'")
        return canonical

    # Fallback: check for obvious matches in already cached games
    best_match = None
    best_ratio = 0.0

    for cached_key, cached_canonical in GAME_CACHE.items():
        if file_extension and not cached_key.endswith(file_extension or "unknown"):
            continue

        cached_name = cached_key.split("_")[0]  # Remove file extension part
        ratio = SequenceMatcher(None, game_name.lower(), cached_name.lower()).ratio()

        if ratio > best_ratio and ratio > 0.75:  # More lenient threshold
            best_ratio = ratio
            best_match = (
                cached_canonical["matched_on"]
                if isinstance(cached_canonical, dict)
                else cached_canonical
            )

    if best_match:
        # Create cache key for this game
        cache_key = f"{game_name}_{file_extension or 'unknown'}"
        GAME_CACHE[cache_key] = best_match
        return best_match

    # Final fallback to original name when IGDB returns None or no good match
    print(f"Using original name: {game_name}")
    return game_name


def main():
    """Main application entry point"""
    root = tk.Tk()

    # Set up modern styling
    style = ttk.Style()
    if "winnative" in style.theme_names():
        style.theme_use("winnative")

    # Create the application
    app = ROMCleanupGUI(root)

    # Center window on screen
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")

    # Perform startup API check
    def startup_api_check():
        app.log_message("ROM Collection Cleanup Tool with IGDB Integration")
        app.log_message("=" * 60)
        app.log_message("Advanced ROM duplicate detection using IGDB database")
        app.log_message("Clipboard functionality available for easy log copying")
        app.log_message("")
        app.log_message("Features:")
        app.log_message(f"• Supports {len(app.ROM_EXTENSIONS)} ROM file formats")
        app.log_message("• IGDB integration for accurate game matching")
        app.log_message("• Multiple operation modes (safe move, backup, delete)")
        app.log_message("• Preserves unique regional releases")
        app.log_message("• Dark theme for comfortable viewing")
        app.log_message("")
        app.log_message("Performing startup API connection check...")
        app.validate_api_credentials()  # This will update the status indicator
        success, message = app.check_api_connection()
        if success:
            app.log_message(f"SUCCESS: {message}")
            app.log_message("Enhanced game matching is available")
        else:
            app.log_message(f"ERROR: {message}")
            app.log_message("Enhanced game matching is disabled")
        app.log_message("Ready to scan ROMs!")

    # Schedule startup API check after GUI is ready
    root.after(1000, startup_api_check)

    # Cleanup when closing
    def on_closing():
        app.restore_console()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    main()
