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