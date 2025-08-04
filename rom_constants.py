"""Shared constants for the ROM cleanup tool."""

# Supported ROM file extensions
ROM_EXTENSIONS = {
    # Archive formats
    ".zip",
    ".7z",
    ".rar",
    # Nintendo systems
    ".nes",
    ".snes",
    ".smc",
    ".sfc",
    ".gb",
    ".gbc",
    ".gba",
    ".nds",
    ".3ds",
    ".cia",
    ".n64",
    ".z64",
    ".v64",
    ".ndd",
    ".gcm",
    ".gcz",
    ".rvz",
    ".wbfs",
    ".xci",
    ".nsp",
    ".vb",
    ".lnx",
    ".ngp",
    ".ngc",
    # Sega systems
    ".md",
    ".gen",
    ".smd",
    ".gg",
    ".sms",
    ".32x",
    ".sat",
    ".gdi",
    # Sony systems
    ".bin",
    ".iso",
    ".cue",
    ".chd",
    ".pbp",
    ".cso",
    ".ciso",
    # PC Engine/TurboGrafx
    ".pce",
    ".sgx",
    # Atari systems
    ".a26",
    ".a78",
    ".st",
    ".d64",
    # Other retro systems
    ".col",
    ".int",
    ".vec",
    ".ws",
    ".wsc",
    # Disk images
    ".img",
    ".ima",
    ".dsk",
    ".adf",
    ".mdf",
    ".nrg",
    # Tape formats
    ".tap",
    ".tzx",
    # Spectrum formats
    ".sna",
    ".z80",
}

# Mapping from file extension to IGDB platform IDs
PLATFORM_MAPPING = {
    # Nintendo systems
    ".nes": [18],
    ".snes": [19],
    ".smc": [19],
    ".sfc": [19],
    ".gb": [33],
    ".gbc": [22],
    ".gba": [24],
    ".nds": [20],
    ".3ds": [37],
    ".cia": [37],
    ".n64": [4],
    ".z64": [4],
    ".v64": [4],
    ".ndd": [4],
    ".gcm": [21],
    ".gcz": [21],
    ".rvz": [5, 21],  # GameCube and Wii
    ".wbfs": [5],  # GameCube and Wii
    ".xci": [130],
    ".nsp": [130],  # Nintendo Switch
    ".vb": [87],
    ".lnx": [28],
    ".ngp": [119],
    ".ngc": [120],
    # Sega systems
    ".md": [29],
    ".gen": [29],
    ".smd": [29],
    ".gg": [35],
    ".sms": [64],
    ".32x": [30],
    ".sat": [32],
    ".gdi": [23],  # Saturn and Dreamcast
    # Sony systems
    ".iso": [7, 8, 9, 21, 38, 39],
    ".bin": [7, 8, 9, 27, 38, 39],
    ".cue": [7, 8, 9, 27, 38, 39],
    ".chd": [7, 8, 9, 27, 38, 39],
    ".pbp": [7, 8],
    ".cso": [7, 8],
    ".ciso": [8, 21],  # PlayStation and GameCube
    ".mdf": [8, 38, 39],
    ".nrg": [8, 38, 39],
    # PC Engine/TurboGrafx
    ".pce": [86],
    ".sgx": [86],
    # Atari systems
    ".a26": [59],
    ".a78": [60],
    ".st": [63],
    # Other systems
    ".col": [68],
    ".int": [67],
    ".vec": [70],
    ".ws": [57],
    ".wsc": [57],
}
