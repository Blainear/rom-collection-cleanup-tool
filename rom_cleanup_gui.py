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
import re
from datetime import datetime

# IGDB API configuration (set as environment variables)
IGDB_CLIENT_ID = os.getenv('IGDB_CLIENT_ID', '')
IGDB_ACCESS_TOKEN = os.getenv('IGDB_ACCESS_TOKEN', '')

class ROMCleanupGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ROM Collection Cleanup Tool v2.0")
        self.root.geometry("800x700")
        self.root.minsize(600, 500)
        
        # Configuration variables
        self.rom_directory = tk.StringVar()
        self.operation_mode = tk.StringVar(value="move")  # move, delete, backup
        self.region_priority = tk.StringVar(value="usa")  # usa, europe, japan, world
        self.keep_japanese_only = tk.BooleanVar(value=True)
        self.keep_europe_only = tk.BooleanVar(value=True)
        self.custom_extensions = tk.StringVar()
        self.create_backup = tk.BooleanVar(value=False)
        self.preserve_subdirs = tk.BooleanVar(value=True)
        
        self.ROM_EXTENSIONS = {'.zip', '.7z', '.rar', '.nes', '.snes', '.smc', '.sfc', 
                              '.gb', '.gbc', '.gba', '.nds', '.n64', '.z64', '.v64',
                              '.md', '.gen', '.smd', '.bin', '.iso', '.cue', '.chd',
                              '.pbp', '.cso', '.gcz', '.wbfs', '.rvz',
                              '.gcm', '.ciso', '.mdf', '.nrg'}
        
        # Region patterns
        self.REGION_PATTERNS = {
            'japan': [r'\(J\)', r'\(Japan\)', r'\(JP\)', r'\(JPN\)', r'\[J\]', r'\[Japan\]'],
            'usa': [r'\(U\)', r'\(USA\)', r'\(US\)', r'\[U\]', r'\[USA\]', r'\[US\]'],
            'europe': [r'\(E\)', r'\(Europe\)', r'\(EUR\)', r'\[E\]', r'\[Europe\]'],
            'world': [r'\(W\)', r'\(World\)', r'\[W\]', r'\[World\]']
        }
        
        self.setup_ui()
        
    def setup_ui(self):
        # Create main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Directory selection
        ttk.Label(main_frame, text="ROM Directory:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(0, weight=1)
        
        ttk.Entry(dir_frame, textvariable=self.rom_directory, width=50).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(dir_frame, text="Browse", command=self.browse_directory).grid(row=0, column=1)
        
        # Create notebook for organized options
        notebook = ttk.Notebook(main_frame)
        notebook.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(2, weight=1)
        
        # Basic Options Tab
        basic_frame = ttk.Frame(notebook, padding="10")
        notebook.add(basic_frame, text="Basic Options")
        
        # Operation mode
        ttk.Label(basic_frame, text="Operation Mode:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        mode_frame = ttk.Frame(basic_frame)
        mode_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Radiobutton(mode_frame, text="Move to 'to_delete' folder (Safest)", 
                       variable=self.operation_mode, value="move").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(mode_frame, text="Delete immediately", 
                       variable=self.operation_mode, value="delete").grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(mode_frame, text="Copy to backup folder first", 
                       variable=self.operation_mode, value="backup").grid(row=2, column=0, sticky=tk.W)
        
        # Region priority
        ttk.Label(basic_frame, text="Preferred Region:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        region_frame = ttk.Frame(basic_frame)
        region_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(0, 10))
        
        ttk.Radiobutton(region_frame, text="USA", variable=self.region_priority, value="usa").grid(row=0, column=0, sticky=tk.W)
        ttk.Radiobutton(region_frame, text="Europe", variable=self.region_priority, value="europe").grid(row=0, column=1, sticky=tk.W, padx=(20, 0))
        ttk.Radiobutton(region_frame, text="Japan", variable=self.region_priority, value="japan").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        ttk.Radiobutton(region_frame, text="World", variable=self.region_priority, value="world").grid(row=0, column=3, sticky=tk.W, padx=(20, 0))
        
        # Preservation options
        ttk.Label(basic_frame, text="Preservation Options:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        ttk.Checkbutton(basic_frame, text="Keep Japanese-only releases", 
                       variable=self.keep_japanese_only).grid(row=5, column=0, sticky=tk.W)
        ttk.Checkbutton(basic_frame, text="Keep Europe-only releases", 
                       variable=self.keep_europe_only).grid(row=6, column=0, sticky=tk.W)
        ttk.Checkbutton(basic_frame, text="Preserve subdirectory structure", 
                       variable=self.preserve_subdirs).grid(row=7, column=0, sticky=tk.W)
        
        # Advanced Options Tab
        advanced_frame = ttk.Frame(notebook, padding="10")
        notebook.add(advanced_frame, text="Advanced")
        
        ttk.Label(advanced_frame, text="Custom File Extensions:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        ttk.Entry(advanced_frame, textvariable=self.custom_extensions, width=40).grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Label(advanced_frame, text="(comma-separated, e.g. .rom,.img)", font=("TkDefaultFont", 8)).grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        ttk.Checkbutton(advanced_frame, text="Create backup before any operations", 
                       variable=self.create_backup).grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # Current extensions display
        ttk.Label(advanced_frame, text="Supported Extensions:").grid(row=4, column=0, sticky=tk.W, pady=(10, 5))
        ext_text = scrolledtext.ScrolledText(advanced_frame, height=6, width=50)
        ext_text.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        ext_text.insert(tk.END, ", ".join(sorted(self.ROM_EXTENSIONS)))
        ext_text.config(state=tk.DISABLED)
        advanced_frame.columnconfigure(0, weight=1)
        
        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(10, 0))
        
        ttk.Button(button_frame, text="Scan ROMs", command=self.scan_roms, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Preview Changes", command=self.preview_changes).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="Execute", command=self.execute_operation).pack(side=tk.LEFT)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 5))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(main_frame, textvariable=self.status_var).grid(row=5, column=0, columnspan=3, pady=(0, 5))
        
        # Results/Log area
        ttk.Label(main_frame, text="Results:").grid(row=6, column=0, sticky=tk.W, pady=(10, 5))
        self.log_text = scrolledtext.ScrolledText(main_frame, height=12, width=80)
        self.log_text.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 0))
        main_frame.rowconfigure(7, weight=1)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select ROM Directory")
        if directory:
            self.rom_directory.set(directory)
            
    def log_message(self, message):
        """Add message to log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def get_region(self, filename):
        """Extract region from filename based on common ROM naming patterns."""
        filename_upper = filename.upper()
        
        for region, patterns in self.REGION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, filename_upper):
                    return region
        return 'unknown'
        
    def get_base_name(self, filename):
        """Extract the base game name by removing region tags, revision info, etc."""
        base = os.path.splitext(filename)[0]
        base = re.sub(r'\s*[\(\[].*?[\)\]]', '', base)
        base = re.sub(r'\s*(Rev|v|Ver|Version)\s*\d+.*$', '', base, flags=re.IGNORECASE)
        base = re.sub(r'\s*-\s*\d+$', '', base)
        base = re.sub(r'\s+', ' ', base).strip()
        return base
        
    def scan_roms(self):
        if not self.rom_directory.get():
            messagebox.showerror("Error", "Please select a ROM directory first.")
            return
            
        def scan_thread():
            self.status_var.set("Scanning ROMs...")
            self.progress_var.set(0)
            self.log_text.delete(1.0, tk.END)
            
            try:
                # Get extensions
                extensions = self.ROM_EXTENSIONS.copy()
                if self.custom_extensions.get():
                    custom_exts = {ext.strip().lower() for ext in self.custom_extensions.get().split(',')}
                    extensions.update(custom_exts)
                
                # Scan directory
                rom_groups = defaultdict(list)
                directory = Path(self.rom_directory.get())
                
                all_files = list(directory.rglob('*'))
                total_files = len(all_files)
                
                for i, file_path in enumerate(all_files):
                    if file_path.is_file() and file_path.suffix.lower() in extensions:
                        filename = file_path.name
                        base_name = self.get_base_name(filename)
                        region = self.get_region(filename)
                        rom_groups[base_name].append((file_path, region))
                    
                    # Update progress
                    if i % 10 == 0:  # Update every 10 files
                        progress = (i / total_files) * 100
                        self.progress_var.set(progress)
                        self.root.update_idletasks()
                
                self.rom_groups = rom_groups
                self.progress_var.set(100)
                
                # Log results
                total_games = len(rom_groups)
                total_roms = sum(len(roms) for roms in rom_groups.values())
                
                self.log_message(f"Scan completed!")
                self.log_message(f"Found {total_roms} ROM files representing {total_games} unique games")
                self.log_message(f"Supported extensions: {', '.join(sorted(extensions))}")
                
                # Show some examples
                self.log_message("\nExamples found:")
                for i, (game_name, roms) in enumerate(list(rom_groups.items())[:5]):
                    regions = [region for _, region in roms]
                    self.log_message(f"  {game_name}: {len(roms)} versions ({', '.join(set(regions))})")
                
                if total_games > 5:
                    self.log_message(f"  ... and {total_games - 5} more games")
                
                self.status_var.set(f"Scan complete: {total_games} games found")
                
            except Exception as e:
                self.log_message(f"Error during scan: {str(e)}")
                self.status_var.set("Scan failed")
                
        # Run scan in separate thread
        threading.Thread(target=scan_thread, daemon=True).start()
        
    def preview_changes(self):
        if not hasattr(self, 'rom_groups'):
            messagebox.showerror("Error", "Please scan ROMs first.")
            return
            
        self.log_message("\n" + "="*50)
        self.log_message("PREVIEW - No changes will be made")
        self.log_message("="*50)
        
        to_remove = self.find_duplicates_to_remove()
        
        if not to_remove:
            self.log_message("No duplicates found to remove based on current settings.")
            self.status_var.set("No changes needed")
            return
            
        self.log_message(f"\nSummary: {len(to_remove)} ROM(s) would be processed")
        self.log_message(f"Operation mode: {self.operation_mode.get()}")
        self.log_message(f"Preferred region: {self.region_priority.get()}")
        
        if self.operation_mode.get() == "move":
            self.log_message(f"\nFiles would be moved to: {self.rom_directory.get()}/to_delete/")
        elif self.operation_mode.get() == "backup":
            self.log_message(f"\nFiles would be backed up to: {self.rom_directory.get()}/backup_[timestamp]/")
            
        self.log_message("\nFiles that would be processed:")
        for file_path in to_remove:
            self.log_message(f"  {file_path}")
            
        self.status_var.set(f"Preview complete: {len(to_remove)} files would be processed")
        
    def find_duplicates_to_remove(self):
        """Find ROMs to remove based on current settings"""
        to_remove = []
        preferred_region = self.region_priority.get()
        
        for base_name, roms in self.rom_groups.items():
            if len(roms) <= 1:
                continue
                
            # Group by region
            regions = defaultdict(list)
            for file_path, region in roms:
                regions[region].append(file_path)
            
            # Determine what to keep and what to remove
            if preferred_region in regions:
                # We have preferred region, remove others (with exceptions)
                for region, files in regions.items():
                    if region != preferred_region:
                        # Check preservation rules
                        should_preserve = False
                        
                        if region == 'japan' and self.keep_japanese_only.get():
                            # Only preserve if it's truly Japanese-only
                            if len(regions) == 1 or (len(regions) == 2 and 'unknown' in regions):
                                should_preserve = True
                                
                        elif region == 'europe' and self.keep_europe_only.get():
                            # Only preserve if it's truly Europe-only
                            if len(regions) == 1 or (len(regions) == 2 and 'unknown' in regions):
                                should_preserve = True
                        
                        if not should_preserve:
                            to_remove.extend(files)
                            self.log_message(f"Game: {base_name}")
                            self.log_message(f"  Keeping {preferred_region} version(s): {[p.name for p in regions[preferred_region]]}")
                            self.log_message(f"  Removing {region} version(s): {[p.name for p in files]}")
                        else:
                            self.log_message(f"Game: {base_name} - Preserving {region}-only release")
            
        return to_remove
        
    def execute_operation(self):
        if not hasattr(self, 'rom_groups'):
            messagebox.showerror("Error", "Please scan ROMs first.")
            return
            
        to_remove = self.find_duplicates_to_remove()
        
        if not to_remove:
            messagebox.showinfo("Info", "No duplicates found to remove based on current settings.")
            return
            
        # Confirm operation
        mode_text = {
            "move": "move to 'to_delete' folder",
            "delete": "permanently delete",
            "backup": "backup and then delete"
        }
        
        result = messagebox.askyesno(
            "Confirm Operation", 
            f"This will {mode_text[self.operation_mode.get()]} {len(to_remove)} ROM files.\n\nDo you want to continue?"
        )
        
        if not result:
            return
            
        def execute_thread():
            try:
                self.progress_var.set(0)
                total_files = len(to_remove)
                
                if self.operation_mode.get() == "move":
                    self.move_to_safe_folder(to_remove)
                elif self.operation_mode.get() == "backup":
                    self.backup_and_delete(to_remove)
                else:  # delete
                    self.delete_files(to_remove)
                    
                self.progress_var.set(100)
                self.status_var.set("Operation completed successfully")
                self.log_message("\nOperation completed!")
                
            except Exception as e:
                self.log_message(f"Error during operation: {str(e)}")
                self.status_var.set("Operation failed")
                messagebox.showerror("Error", f"Operation failed: {str(e)}")
                
        threading.Thread(target=execute_thread, daemon=True).start()
        
    def move_to_safe_folder(self, to_remove):
        safe_folder = Path(self.rom_directory.get()) / "to_delete"
        safe_folder.mkdir(exist_ok=True)
        
        self.log_message(f"\nMoving {len(to_remove)} files to safe folder...")
        
        for i, file_path in enumerate(to_remove):
            try:
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
                
    def backup_and_delete(self, to_remove):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_folder = Path(self.rom_directory.get()) / f"backup_{timestamp}"
        backup_folder.mkdir(exist_ok=True)
        
        self.log_message(f"\nBacking up {len(to_remove)} files...")
        
        # First backup
        for i, file_path in enumerate(to_remove):
            try:
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
            try:
                file_path.unlink()
                self.log_message(f"  Deleted: {file_path.name}")
                
                # Update progress
                progress = ((i + 1) / len(to_remove)) * 100
                self.progress_var.set(progress)
                self.root.update_idletasks()
                
            except Exception as e:
                self.log_message(f"  Error deleting {file_path}: {e}")

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
    
    root.mainloop()

if __name__ == '__main__':
    main()