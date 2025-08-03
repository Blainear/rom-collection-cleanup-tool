35
2. Install dependencies: `pip install -r requirements.txt`
36
3. Set up IGDB API credentials (optional but recommended)
37
​
38
### IGDB API Setup (Optional)
39
​
40
1. **Register a Twitch developer application**
41
 - Visit the [Twitch Developers console](https://dev.twitch.tv/console)
42
 - Sign in and create a new application to obtain your **Client ID** and **Client Secret**
43
 - Follow the [IGDB Getting Started guide](https://api-docs.igdb.com/#getting-started) for detailed instructions
44
2. **Request an access token** using your credentials:
45
 ```bash
46
 curl -X POST https://id.twitch.tv/oauth2/token \
47
 -d 'client_id=YOUR_CLIENT_ID' \
48
 -d 'client_secret=YOUR_CLIENT_SECRET' \
49
 -d 'grant_type=client_credentials'
50
 ```
51
​
52
## Usage
53
​
54
### Command-Line Interface (CLI)
55
​
56
Invoke the script with the target directory:
57
​
58
```bash
59
python rom_cleanup.py /path/to/roms
60
```
61
​
62
Preview actions without modifying files:
63
​
64
```bash
65
python rom_cleanup.py /path/to/roms --dry-run
66
```
67
​
68
Move duplicates to a review folder instead of deleting:
69
​
70
```bash
71
python rom_cleanup.py /path/to/roms --move-to-folder
72
```
73
​
74
Include additional file extensions:
75
​
76
```bash
77
python rom_cleanup.py /path/to/roms --extensions 7z,zip
78
```
79
​
80
### Graphical User Interface (GUI)
81
​
82
Launch the GUI with:
83
​
84
```bash
85
python rom_cleanup_gui.py
86
```
87
​
88
The interface performs a startup IGDB API check and includes a **Check API** button for manual testing. During scanning or cleanup operations, use the **Stop Process** button to halt processing safely.
89
​