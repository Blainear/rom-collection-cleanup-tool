#!/usr/bin/env python3
"""
ROM Collection Cleanup Tool - GUI Version

A user-friendly GUI tool for managing ROM collections by removing duplicates
based on region preferences while preserving unique releases.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import shutil
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import json
import time
import hashlib
import logging
from rom_utils import get_region, get_base_name
try:
    import requests
except ImportError:
    requests = None
    print("The 'requests' library is required for IGDB features. Please install it to enable them.")
from difflib import SequenceMatcher

# IGDB configuration
GAME_CACHE = {}
CACHE_FILE = Path("game_cache.json")

# Platform mapping for IGDB
PLATFORM_MAPPING = {
    '.nes': [18],      # Nintendo Entertainment System
    '.snes': [19],     # Super Nintendo Entertainment System  
    '.smc': [19],
    '.sfc': [19],
    '.gb': [33],       # Game Boy
    '.gbc': [22],      # Game Boy Color
    '.gba': [24],      # Game Boy Advance
    '.nds': [20],      # Nintendo DS
    '.n64': [4],       # Nintendo 64
    '.z64': [4],
    '.v64': [4],
    '.md': [29],       # Sega Mega Drive/Genesis
    '.gen': [29],
    '.smd': [29],
    '.gcm': [21],      # GameCube
    '.gcz': [21],
    '.ciso': [21],
    '.iso': [21, 38, 39], # Multiple platforms (GameCube, PlayStation, PlayStation 2)
    '.wbfs': [5],      # Wii
    '.rvz': [5],
    '.pbp': [7],       # PlayStation Portable
    '.cso': [7],
    '.chd': [27, 38, 39], # Multiple CD-based platforms
    '.cue': [27, 38, 39],
    '.bin': [27, 38, 39],
    '.mdf': [38, 39],  # PlayStation, PlayStation 2
    '.nrg': [38, 39]
}

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
        self.root.title("ROM Collection Cleanup Tool v2.0")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # Console redirection setup (will be activated after UI setup)
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        self.console_redirector = None
        
        # Process control
        self.current_process = None
        self.process_stop_requested = False
        
        # Configuration variables
        self.rom_directory = tk.StringVar()
        self.operation_mode = tk.StringVar(value="move")  # move, delete, backup
        self.region_priority = tk.StringVar(value="usa")  # usa, europe, japan, world
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
        
        self.ROM_EXTENSIONS = {'.zip', '.7z', '.rar', '.nes', '.snes', '.smc', '.sfc', 
                              '.gb', '.gbc', '.gba', '.nds', '.n64', '.z64', '.v64',
                              '.md', '.gen', '.smd', '.bin', '.iso', '.cue', '.chd',
                              '.pbp', '.cso', '.gcz', '.wbfs', '.rvz',
                              '.gcm', '.ciso', '.mdf', '.nrg'}
        
        self.setup_dark_theme()
        self.setup_ui()
        
        # Set up console redirection after UI is ready
        self.setup_console_redirection()
        
    def setup_dark_theme(self):
        """Configure dark theme for the GUI"""
        self.root.configure(bg='#2b2b2b')

        self.style = ttk.Style()
        self.style.theme_use('clam')

        style_configs = {
            'Dark.TFrame': {
                'background': '#2b2b2b',
                'borderwidth': 1,
                'relief': 'flat'
            },
            'Dark.TLabel': {
                'background': '#2b2b2b',
                'foreground': '#ffffff',
                'font': ('Segoe UI', 9)
            },
            'Title.TLabel': {
                'background': '#2b2b2b',
                'foreground': '#4a9eff',
                'font': ('Segoe UI', 12, 'bold')
            },
            'Dark.TEntry': {
                'fieldbackground': '#404040',
                'background': '#404040',
                'foreground': '#ffffff',
                'borderwidth': 1,
                'insertcolor': '#ffffff',
                'selectbackground': '#4a9eff',
                'selectforeground': '#ffffff'
            },
            'Dark.TButton': {
                'background': '#404040',
                'foreground': '#ffffff',
                'borderwidth': 1,
                'focuscolor': '#4a9eff',
                'font': ('Segoe UI', 9)
            },
            'Accent.TButton': {
                'background': '#4a9eff',
                'foreground': '#ffffff',
                'borderwidth': 1,
                'font': ('Segoe UI', 9, 'bold')
            },
            'Dark.TCheckbutton': {
                'background': '#2b2b2b',
                'foreground': '#ffffff',
                'focuscolor': '#4a9eff',
                'font': ('Segoe UI', 9)
            },
            'Dark.TRadiobutton': {
                'background': '#2b2b2b',
                'foreground': '#ffffff',
                'focuscolor': '#4a9eff',
                'font': ('Segoe UI', 9)
            },
            'Dark.TCombobox': {
                'fieldbackground': '#404040',
                'background': '#404040',
                'foreground': '#ffffff',
                'borderwidth': 1,
                'selectbackground': '#4a9eff',
                'selectforeground': '#ffffff'
            },
            'Dark.Horizontal.TProgressbar': {
                'background': '#4a9eff',
                'troughcolor': '#404040',
                'borderwidth': 1,
                'lightcolor': '#4a9eff',
                'darkcolor': '#357abd'
            },
            'Dark.TNotebook': {
                'background': '#2b2b2b',
                'borderwidth': 1,
                'tabmargins': [2, 5, 2, 0]
            },
            'Dark.TNotebook.Tab': {
                'background': '#404040',
                'foreground': '#ffffff',
                'padding': [12, 8],
                'font': ('Segoe UI', 9)
            }
        }

        for style_name, options in style_configs.items():
            self.style.configure(style_name, **options)

        style_maps = {
            'Dark.TButton': {
                'background': [('active', '#4a9eff'), ('pressed', '#357abd')]
            },
            'Accent.TButton': {
                'background': [('active', '#357abd'), ('pressed', '#2d5a87')]
            },
            'Dark.TNotebook.Tab': {
                'background': [('selected', '#4a9eff'), ('active', '#505050')]
            }
        }

        for style_name, maps in style_maps.items():
            for option, values in maps.items():
                self.style.map(style_name, **{option: values})
    
    def setup_ui(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10", style="Dark.TFrame")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Directory selection
        ttk.Label(main_frame, text="ROM Directory:", style="Dark.TLabel").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        dir_frame = ttk.Frame(main_frame, style="Dark.TFrame")
        dir_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(dir_frame, textvariable=self.rom_directory, width=50, style="Dark.TEntry").grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory, style="Dark.TButton").grid(row=0, column=1)
        
        # Create notebook for organized options
        notebook = ttk.Notebook(main_frame, style="Dark.TNotebook")
        notebook.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(2, weight=1)
        
        # Basic Options Tab
        basic_frame = ttk.Frame(notebook, padding="10", style="Dark.TFrame")
        notebook.add(basic_frame, text="Basic Options")
        
        # Operation mode
        ttk.Label(basic_frame, text="Operation Mode:", style="Dark.TLabel").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        mode_frame = ttk.Frame(basic_frame, style="Dark.TFrame")
        mode_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="Move to 'to_delete' folder (Safest)", 
                       variable=self.operation_mode, value="move", style="Dark.TRadiobutton").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(mode_frame, text="Delete immediately", 
                       variable=self.operation_mode, value="delete", style="Dark.TRadiobutton").grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(mode_frame, text="Copy to backup folder first", 
                       variable=self.operation_mode, value="backup", style="Dark.TRadiobutton").grid(row=2, column=0, sticky=tk.W)
        
        # Region priority
        ttk.Label(basic_frame, text="Preferred Region:", style="Dark.TLabel").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        region_frame = ttk.Frame(basic_frame, style="Dark.TFrame")
        region_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Radiobutton(region_frame, text="USA", variable=self.region_priority, value="usa", style="Dark.TRadiobutton").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(region_frame, text="Europe", variable=self.region_priority, value="europe", style="Dark.TRadiobutton").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        ttk.Radiobutton(region_frame, text="Japan", variable=self.region_priority, value="japan", style="Dark.TRadiobutton").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        ttk.Radiobutton(region_frame, text="World", variable=self.region_priority, value="world", style="Dark.TRadiobutton").grid(row=0, column=3, sticky=tk.W, padx=(20, 0))
        
        # Preservation options
        ttk.Label(basic_frame, text="Preservation Options:", style="Dark.TLabel").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        ttk.Checkbutton(basic_frame, text="Keep Japanese-only releases", 
                       variable=self.keep_japanese_only, style="Dark.TCheckbutton").grid(row=5, column=0, sticky=tk.W)
        ttk.Checkbutton(basic_frame, text="Keep Europe-only releases", 
                       variable=self.keep_europe_only, style="Dark.TCheckbutton").grid(row=6, column=0, sticky=tk.W)
        ttk.Checkbutton(basic_frame, text="Preserve subdirectory structure", 
                       variable=self.preserve_subdirs, style="Dark.TCheckbutton").grid(row=7, column=0, sticky=tk.W)
        
        # Advanced Options Tab
        advanced_frame = ttk.Frame(notebook, padding="10", style="Dark.TFrame")
        notebook.add(advanced_frame, text="Advanced")
         
        # IGDB API Configuration
        ttk.Label(advanced_frame, text="IGDB API Configuration:", style="Title.TLabel").grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(advanced_frame, text="Client ID:", style="Dark.TLabel").grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(advanced_frame, textvariable=self.igdb_client_id, width=50, style="Dark.TEntry").grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(advanced_frame, text="Access Token:", style="Dark.TLabel").grid(row=3, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(advanced_frame, textvariable=self.igdb_access_token, width=50, style="Dark.TEntry", show="*").grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # API Status indicator
        ttk.Label(advanced_frame, text="API Status:", style="Dark.TLabel").grid(row=5, column=0, sticky=tk.W, pady=(5, 0))
        self.api_status_label = ttk.Label(advanced_frame, textvariable=self.api_status_var, style="Dark.TLabel")
        self.api_status_label.grid(row=6, column=0, sticky=tk.W, pady=(0, 10))
        
        # Bind validation to credential changes
        self.igdb_client_id.trace('w', lambda *args: self.validate_api_credentials())
        self.igdb_access_token.trace('w', lambda *args: self.validate_api_credentials())
        
        # Add a button to show detailed API error info
        ttk.Button(advanced_frame, text="Show API Details", command=self.show_api_details, 
                  style="Dark.TButton").grid(row=6, column=1, sticky=tk.W, pady=(0, 10))
        
        ttk.Label(advanced_frame, text="Get your IGDB API credentials from: https://api.igdb.com/", 
                 font=("Segoe UI", 8), style="Dark.TLabel").grid(row=7, column=0, sticky=tk.W, pady=(0, 15))
        
        # Custom File Extensions
        ttk.Label(advanced_frame, text="Custom File Extensions:", style="Dark.TLabel").grid(row=8, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(advanced_frame, textvariable=self.custom_extensions, width=40, style="Dark.TEntry").grid(row=9, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(advanced_frame, text="(comma-separated, e.g. .rom,.img)", font=("Segoe UI", 8), style="Dark.TLabel").grid(row=10, column=0, sticky=tk.W, pady=(0, 10))
        
        ttk.Checkbutton(advanced_frame, text="Create backup before any operations", 
                       variable=self.create_backup, style="Dark.TCheckbutton").grid(row=11, column=0, sticky=tk.W, pady=(0, 10))
        
        # Current extensions display
        ttk.Label(advanced_frame, text="Supported Extensions:", style="Dark.TLabel").grid(row=12, column=0, sticky=tk.W, pady=(10, 5))
        ext_text = scrolledtext.ScrolledText(advanced_frame, height=6, width=50, bg='#404040', fg='#ffffff', 
                                           insertbackground='#ffffff', selectbackground='#4a9eff', selectforeground='#ffffff',
                                           font=('Consolas', 9))
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
        
        ttk.Button(main_buttons_frame, text="Scan ROMs", command=self.scan_roms, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(main_buttons_frame, text="Preview Changes", command=self.preview_changes_button, style="Dark.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(main_buttons_frame, text="Execute", command=self.execute_operation, style="Dark.TButton").pack(side=tk.LEFT)
        
        # Control buttons
        control_buttons_frame = ttk.Frame(button_frame, style="Dark.TFrame")
        control_buttons_frame.pack(side=tk.RIGHT)
        
        ttk.Button(control_buttons_frame, text="Check API", command=self.force_api_check, 
                  style="Dark.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(control_buttons_frame, text="Stop Process", command=self.stop_process, 
                  style="Dark.TButton").pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100, style="Dark.Horizontal.TProgressbar")
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var, style="Dark.TLabel").grid(row=5, column=0, columnspan=3, pady=(0, 5))
        
        # Results/Log area
        ttk.Label(main_frame, text="Results:", style="Dark.TLabel").grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
        self.log_text = scrolledtext.ScrolledText(main_frame, height=12, width=80, bg='#1e1e1e', fg='#ffffff',
                                                insertbackground='#ffffff', selectbackground='#4a9eff', selectforeground='#ffffff',
                                                font=('Consolas', 9))
        self.log_text.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
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
        directory = filedialog.askdirectory(title="Select ROM Directory")
        if directory:
            self.rom_directory.set(directory)
            self.log_message(f"Directory selected: {directory}")
            
    def check_api_connection(self):
        """Check IGDB API connection and return status"""
        client_id = self.igdb_client_id.get().strip()
        access_token = self.igdb_access_token.get().strip()
        
        if not client_id:
            return False, "IGDB Client ID not configured - enter your credentials in Advanced tab"
        elif not access_token:
            return False, "IGDB Access Token not configured - enter your credentials in Advanced tab"
        elif not requests:
            return False, "requests library not available"
        
        try:
            headers = {
                'Client-ID': client_id,
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            response = requests.post(
                'https://api.igdb.com/v4/games',
                headers=headers,
                data='fields name; limit 1;',
                timeout=10
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
                        return False, "Authentication failed (401) - check Client ID and Access Token"
                except:
                    return False, "Authentication failed (401) - check Client ID and Access Token"
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
            self.api_status_var.set("✅ Connected")
            self.api_status_color.set("#51cf66")  # Green
        else:
            # Show the specific error message
            error_text = f"❌ {message}"
            if len(error_text) > 50:  # Truncate long error messages
                error_text = error_text[:47] + "..."
            self.api_status_var.set(error_text)
            self.api_status_color.set("#ff6b6b")  # Red
        
        # Update the status label if it exists
        if hasattr(self, 'api_status_label'):
            self.api_status_label.config(
                text=self.api_status_var.get(),
                foreground=self.api_status_color.get()
            )
    
    def force_api_check(self):
        """Force API connection check"""
        self.log_message("\n" + "="*50)
        self.log_message("FORCING API CONNECTION CHECK")
        self.log_message("="*50)
        
        success, message = self.check_api_connection()
        
        if success:
            self.log_message(f"✅ {message}")
            self.log_message("Enhanced game matching is available")
        else:
            self.log_message(f"❌ {message}")
            self.log_message("Enhanced game matching is disabled")
            
        self.log_message("="*50)
    
    def show_api_details(self):
        """Show detailed API connection information"""
        client_id = self.igdb_client_id.get().strip()
        access_token = self.igdb_access_token.get().strip()
        
        self.log_message("\n" + "="*50)
        self.log_message("DETAILED API CONNECTION INFO")
        self.log_message("="*50)
        
        # Show credential status (masked)
        if client_id:
            masked_client_id = client_id[:4] + "*" * (len(client_id) - 8) + client_id[-4:] if len(client_id) > 8 else "****"
            self.log_message(f"Client ID: {masked_client_id}")
        else:
            self.log_message("Client ID: NOT SET")
            
        if access_token:
            masked_token = access_token[:4] + "*" * (len(access_token) - 8) + access_token[-4:] if len(access_token) > 8 else "****"
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
                'Client-ID': client_id,
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            self.log_message("Testing connection to IGDB API...")
            response = requests.post(
                'https://api.igdb.com/v4/games',
                headers=headers,
                data='fields name; limit 1;',
                timeout=10
            )
            
            self.log_message(f"Response Status Code: {response.status_code}")
            self.log_message(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                self.log_message("✅ API connection successful!")
                self.log_message("Your credentials are working correctly.")
            elif response.status_code == 401:
                self.log_message("❌ Authentication failed (401)")
                self.log_message("This usually means:")
                self.log_message("  - Client ID is incorrect")
                self.log_message("  - Access Token is incorrect or expired")
                self.log_message("  - You need to regenerate your Access Token")
            elif response.status_code == 429:
                self.log_message("❌ Rate limit exceeded (429)")
                self.log_message("Too many requests - wait a moment and try again")
            else:
                self.log_message(f"❌ Unexpected response: {response.status_code}")
                self.log_message(f"Response text: {response.text[:200]}...")
                
        except requests.exceptions.ConnectionError as e:
            self.log_message("❌ Connection error")
            self.log_message("Check your internet connection")
        except requests.exceptions.Timeout as e:
            self.log_message("❌ Request timeout")
            self.log_message("The API request took too long")
        except Exception as e:
            self.log_message(f"❌ Unexpected error: {e}")
        
        self.log_message("="*50)
    
    def stop_process(self):
        """Stop current process without closing the app"""
        if self.current_process and self.current_process.is_alive():
            self.process_stop_requested = True
            self.log_message("🛑 Stop requested - waiting for current operation to complete...")
            self.status_var.set("Stopping...")
        else:
            self.log_message("ℹ️ No active process to stop")
    
    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def scan_roms(self):
        if not self.rom_directory.get():
            messagebox.showerror("Error", "Please select a ROM directory first.")
            return
            
        def scan_thread():
            self.status_var.set("Scanning ROMs...")
            self.progress_var.set(0)
            self.log_text.delete(1.0, tk.END)
            
            self.log_message("\n" + "="*50)
            self.log_message("STARTING ROM SCAN")
            self.log_message("="*50)
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
                self.log_message(f"✅ {message}")
                self.log_message("Enhanced game matching is available")
            else:
                self.log_message(f"❌ {message}")
                self.log_message("Enhanced game matching is disabled")
            
            self.log_message("-" * 50)
            
            try:
                # Initialize IGDB cache (clears old cache for fresh results)
                self.log_message("Initializing IGDB cache...")
                load_game_cache()
                
                # Get extensions
                extensions = self.ROM_EXTENSIONS.copy()
                if self.custom_extensions.get():
                    custom_exts = {ext.strip().lower() for ext in self.custom_extensions.get().split(',')}
                    extensions.update(custom_exts)
                
                # Scan directory
                self.log_message("Scanning directory structure...")
                directory = Path(self.rom_directory.get())
                all_files = list(directory.rglob('*'))
                self.log_message(f"Found {len(all_files)} total files")
                
                rom_files = [f for f in all_files if f.is_file() and f.suffix.lower() in extensions]
                self.log_message(f"Found {len(rom_files)} ROM files")
                
                if not rom_files:
                    self.log_message("ERROR: No ROM files found in the selected directory.")
                    self.status_var.set("No ROM files found")
                    return
                
                # Group ROMs by canonical name
                rom_groups = defaultdict(list)
                total_files = len(rom_files)
                self.progress_var.set(0)
                
                self.log_message(f"Processing {total_files} ROM files...")
                self.log_message("Analyzing each file for regional variants...")
                
                for i, file_path in enumerate(rom_files):
                    # Check if stop was requested
                    if self.process_stop_requested:
                        self.log_message("🛑 Process stopped by user request")
                        self.status_var.set("Process stopped")
                        return
                    
                    if file_path.is_file() and file_path.suffix.lower() in extensions:
                        filename = file_path.name
                        base_name = get_base_name(filename)
                        file_extension = file_path.suffix.lower()
                        region = get_region(filename)
                        
                        # Log every 10th file or first/last files to avoid spam
                        if i == 0 or i == total_files - 1 or (i + 1) % 10 == 0:
                            self.log_message(f"[{i+1}/{total_files}] Processing: {filename}")
                            self.log_message(f"   Base name: {base_name}")
                            self.log_message(f"   Region: {region}")
                        
                        # Get user credentials for API calls
                        client_id = self.igdb_client_id.get().strip()
                        access_token = self.igdb_access_token.get().strip()
                        
                        canonical_name = get_canonical_name(base_name, file_extension, client_id, access_token)
                        rom_groups[canonical_name].append((file_path, region, base_name))
                    
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
                    self.log_message("\n✅ No duplicates found! Your collection is already clean.")
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
            # If called without arguments, try to get the data from current state
            if hasattr(self, 'rom_groups'):
                to_remove = self.find_duplicates_to_remove(self.rom_groups)
            else:
                self.log_message("ERROR: No files to preview (no rom_groups available)")
                self.status_var.set("Preview failed")
                return
            
        if not to_remove:
            self.log_message("No duplicates found to remove based on current settings.")
            self.status_var.set("No changes needed")
            return
            
        preview_text = f"\nPREVIEW - Files to be removed:\n"
        preview_text += "=" * 50 + "\n"
        
        for file_path in to_remove:
            preview_text += f"  {file_path.name}\n"
        
        preview_text += f"\nTotal: {len(to_remove)} files"
        
        self.log_message(preview_text)
        self.status_var.set(f"Found {len(to_remove)} duplicates")
    
    def preview_changes_button(self):
        """Button handler for preview changes - calls preview_changes with current data"""
        try:
            if not hasattr(self, 'rom_groups'):
                messagebox.showerror("Error", "Please scan ROMs first.")
                return
                
            self.preview_changes()  # Call without arguments, let preview_changes handle it
        except Exception as e:
            self.log_message(f"ERROR in preview_changes_button: {e}")
            self.status_var.set("Preview failed")
            messagebox.showerror("Error", f"Preview failed: {e}")
    
    def find_duplicates_to_remove(self, rom_groups):
        """Find which files should be removed based on region preferences"""
        try:
            to_remove = []
            
            for canonical_name, roms in rom_groups.items():
                if len(roms) == 1:
                    continue  # No duplicates
                    
                # Sort by region priority
                region_priority = self.region_priority.get()
                if region_priority == "usa":
                    priority_order = ["usa", "world", "europe", "japan"]
                elif region_priority == "europe":
                    priority_order = ["europe", "world", "usa", "japan"]
                elif region_priority == "japan":
                    priority_order = ["japan", "world", "usa", "europe"]
                else:  # world
                    priority_order = ["world", "usa", "europe", "japan"]
                
                # Find the best version to keep
                best_rom = None
                best_priority = -1
                
                for file_path, region, base_name in roms:
                    try:
                        priority = priority_order.index(region)
                        if priority < best_priority or best_priority == -1:
                            best_rom = file_path
                            best_priority = priority
                    except ValueError:
                        # Unknown region, keep it
                        continue
                
                # Debug logging
                if best_rom:
                    self.log_message(f"Game: {canonical_name}")
                    self.log_message(f"  Keeping: {best_rom.name} (region: {region_priority})")
                
                # If we found a best version, mark others for removal
                if best_rom:
                    for file_path, region, base_name in roms:
                        if file_path != best_rom:
                            # CRITICAL FIX: Never remove USA files when USA is preferred
                            if region_priority == "usa" and region == "usa":
                                self.log_message(f"  SKIPPING USA file: {file_path.name} (USA files should never be removed)")
                                continue
                            
                            # Check if we should keep this version
                            keep = False
                            
                            if region == "japan" and self.keep_japanese_only.get():
                                # Check if this is the only Japanese version
                                japanese_versions = [r for r in roms if r[1] == "japan"]
                                if len(japanese_versions) == 1:
                                    keep = True
                            
                            elif region == "europe" and self.keep_europe_only.get():
                                # Check if this is the only European version
                                european_versions = [r for r in roms if r[1] == "europe"]
                                if len(european_versions) == 1:
                                    keep = True
                            
                            if not keep:
                                to_remove.append(file_path)
                                if best_rom:
                                    self.log_message(f"  Removing: {file_path.name} (region: {region})")
            
            return to_remove
        except Exception as e:
            self.log_message(f"ERROR in find_duplicates_to_remove: {e}")
            return []
    
    def execute_operation(self):
        """Execute the selected operation on found duplicates"""
        if not hasattr(self, 'rom_groups'):
            messagebox.showerror("Error", "No files to process. Please scan ROMs first.")
            return
            
        to_remove = self.find_duplicates_to_remove(self.rom_groups)
        
        if not to_remove:
            messagebox.showinfo("Info", "No duplicates found to remove based on current settings.")
            return
        
        def execute_thread():
            self.status_var.set("Executing operation...")
            self.progress_var.set(0)
            
            operation = self.operation_mode.get()
            self.log_message(f"\nExecuting {operation} operation on {len(to_remove)} files...")
            
            try:
                if operation == "move":
                    self.move_to_safe_folder(to_remove)
                elif operation == "backup":
                    self.backup_and_delete(to_remove)
                else:  # delete
                    self.delete_files(to_remove)
                
                self.log_message("✅ Operation completed successfully!")
                self.status_var.set("Operation completed")
                
            except Exception as e:
                self.log_message(f"❌ Error during operation: {e}")
                self.status_var.set("Operation failed")
        
        # Run in separate thread
        self.current_process = threading.Thread(target=execute_thread)
        self.current_process.start()
    
    def move_to_safe_folder(self, to_remove):
        """Move files to a safe folder instead of deleting"""
        self.log_message(f"\nMoving {len(to_remove)} files to safe folder...")
        
        # Create safe folder
        safe_folder = Path(self.rom_directory.get()) / "to_delete"
        safe_folder.mkdir(exist_ok=True)
        
        for i, file_path in enumerate(to_remove):
            # Check if stop was requested
            if self.process_stop_requested:
                self.log_message("🛑 Process stopped by user request")
                self.status_var.set("Process stopped")
                return
            
            try:
                # Determine destination path
                if self.preserve_subdirs.get():
                    rel_path = file_path.relative_to(Path(self.rom_directory.get()))
                    dest_path = safe_folder / rel_path
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                else:
                    dest_path = safe_folder / file_path.name
                
                shutil.move(str(file_path), str(dest_path))
                self.log_message(f"  Moved: {file_path.name}")
                
                # Update progress
                progress = ((i + 1) / len(to_remove)) * 100
                self.progress_var.set(progress)
                self.root.update_idletasks()
                
            except Exception as e:
                self.log_message(f"  Error moving {file_path}: {e}")
        
        self.log_message(f"Files moved to: {safe_folder}")
    
    def backup_and_delete(self, to_remove):
        """Backup files before deleting"""
        self.log_message(f"\nBacking up {len(to_remove)} files before deletion...")
        
        # Create backup folder
        backup_folder = Path(self.rom_directory.get()) / "backup" / datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder.mkdir(parents=True, exist_ok=True)
        
        # First backup
        for i, file_path in enumerate(to_remove):
            # Check if stop was requested
            if self.process_stop_requested:
                self.log_message("🛑 Process stopped by user request")
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
                self.log_message("🛑 Process stopped by user request")
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
        self.log_message(f"\nDeleting {len(to_remove)} files...")
        
        for i, file_path in enumerate(to_remove):
            # Check if stop was requested
            if self.process_stop_requested:
                self.log_message("🛑 Process stopped by user request")
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
    GAME_CACHE = {}

def save_game_cache():
    """Save game database cache to file."""
    global GAME_CACHE
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(GAME_CACHE, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(GAME_CACHE)} entries to game cache")
    except Exception as e:
        print(f"Warning: Could not save cache: {e}")

def query_igdb_game(game_name, file_extension=None, client_id=None, access_token=None):
    """Query IGDB for game information."""
    if not requests:
        print("ERROR: requests library not available - IGDB integration disabled")
        return None
    
    if not client_id:
        print("ERROR: IGDB_CLIENT_ID not provided - API integration disabled")
        return None
        
    if not access_token:
        print("ERROR: IGDB_ACCESS_TOKEN not provided - API integration disabled")
        return None
    
    cache_key = hashlib.md5(f"{game_name}_{file_extension}".encode()).hexdigest()
    
    if cache_key in GAME_CACHE:
        print(f"Cache hit for: {game_name}")
        return GAME_CACHE[cache_key]
    
    try:
        # Get platform IDs for this file extension
        platform_ids = PLATFORM_MAPPING.get(file_extension, [])
        
        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        # Search for games
        query = f'''
        fields name,alternative_names.name,platforms;
        search "{game_name}";
        limit 15;
        '''
        
        response = requests.post(
            'https://api.igdb.com/v4/games',
            headers=headers,
            data=query
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"IGDB API returned {len(results)} results for: {game_name}")
            
            # Score and rank results
            scored_results = []
            for result in results:
                score = 0
                
                # Check main name similarity
                main_similarity = SequenceMatcher(None, game_name.lower(), result['name'].lower()).ratio()
                if main_similarity >= 0.7:  # Lowered threshold for better matching
                    score += main_similarity
                
                # Check alternative names with lower threshold
                if 'alternative_names' in result:
                    for alt_name in result['alternative_names']:
                        alt_similarity = SequenceMatcher(None, game_name.lower(), alt_name['name'].lower()).ratio()
                        if alt_similarity >= 0.3:  # Lower threshold for alternative names
                            score += alt_similarity * 0.8  # Weight alternative names slightly less
                
                # Platform bonus
                if platform_ids and 'platforms' in result:
                    result_platforms = [p for p in result['platforms']]
                    if any(pid in result_platforms for pid in platform_ids):
                        score += 0.2  # Platform match bonus
                
                if score > 0:
                    scored_results.append((score, result))
            
            # Sort by score and return best match
            if scored_results:
                scored_results.sort(reverse=True, key=lambda x: x[0])
                best_match = scored_results[0][1]
                score = scored_results[0][0]
                print(f"Best match for '{game_name}': '{best_match['name']}' (score: {score:.2f})")
                GAME_CACHE[cache_key] = best_match
                time.sleep(0.25)  # Rate limiting
                return best_match
            else:
                print(f"No good matches found for: {game_name}")
                # Return None to use original name
                return None
                
        elif response.status_code == 401:
            print(f"IGDB API authentication failed (401) - check CLIENT_ID and ACCESS_TOKEN")
        elif response.status_code == 429:
            print(f"IGDB API rate limit exceeded (429) - too many requests")
        else:
            print(f"IGDB API response code: {response.status_code}")
                
        GAME_CACHE[cache_key] = None
        time.sleep(0.25)  # Rate limiting
        return None
        
    except requests.exceptions.ConnectionError as e:
        print(f"IGDB API connection error: No internet connection or IGDB servers unreachable")
        GAME_CACHE[cache_key] = None
        return None
    except requests.exceptions.Timeout as e:
        print(f"IGDB API timeout error: Request took too long")
        GAME_CACHE[cache_key] = None
        return None
    except Exception as e:
        print(f"IGDB API error for '{game_name}': {e}")
        GAME_CACHE[cache_key] = None
        return None

def get_canonical_name(game_name, file_extension=None, client_id=None, access_token=None):
    """Get canonical name using IGDB or fallback to cache/simple matching."""
    print(f"Looking up canonical name for: {game_name} ({file_extension})")
    
    # Try IGDB first
    igdb_result = query_igdb_game(game_name, file_extension, client_id, access_token)
    if igdb_result:
        canonical = igdb_result['name']
        if canonical != game_name:
            print(f"Canonical name: '{game_name}' -> '{canonical}'")
        return canonical
    
    # Fallback to original name when IGDB returns None or no good match
    print(f"Using original name: {game_name}")
    return game_name

def main():
    root = tk.Tk()
    
    # Set up modern styling
    style = ttk.Style()
    if "winnative" in style.theme_names():
        style.theme_use("winnative")
    
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
        app.log_message("🔍 Performing startup API connection check...")
        app.validate_api_credentials()  # This will update the status indicator
        success, message = app.check_api_connection()
        if success:
            app.log_message(f"✅ {message}")
            app.log_message("Enhanced game matching is available")
        else:
            app.log_message(f"❌ {message}")
            app.log_message("Enhanced game matching is disabled")
        app.log_message("Ready to scan ROMs!")
    
    # Schedule startup API check after GUI is ready
    root.after(1000, startup_api_check)
    
    root.mainloop()

if __name__ == '__main__':
    main()
