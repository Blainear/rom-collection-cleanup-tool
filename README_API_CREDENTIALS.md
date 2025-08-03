# IGDB API Credentials Setup

This ROM cleanup tool uses the IGDB (Internet Game Database) API to match regional game name variants. To use this feature, you need to provide your own API credentials.

## How to Get IGDB API Credentials

### 1. Create an IGDB Account
1. Go to [https://api.igdb.com/](https://api.igdb.com/)
2. Click "Sign Up" and create a free account
3. Verify your email address

### 2. Create a New Application
1. After logging in, go to your dashboard
2. Click "Create Application"
3. Fill in the application details:
   - **Name**: ROM Cleanup Tool (or any name you prefer)
   - **Description**: ROM collection cleanup tool
   - **Website**: (optional)
4. Click "Create"

### 3. Get Your Credentials
1. In your application dashboard, you'll see:
   - **Client ID**: A long string of characters
   - **Access Token**: Another long string of characters
2. Copy both values

### 4. Enter Credentials in the Tool
1. Run the ROM cleanup tool
2. Go to the "Advanced" tab
3. Enter your Client ID in the "Client ID" field
4. Enter your Access Token in the "Access Token" field
5. Click "Check API" to verify your credentials work

## Security Notes
- Your API credentials are stored only in the GUI and are not saved to disk
- The credentials are used only for API calls to IGDB
- Never share your credentials publicly
- You can regenerate your access token from the IGDB dashboard if needed

## API Usage Limits
- IGDB provides free API access with reasonable rate limits
- The tool includes rate limiting to stay within these limits
- If you hit rate limits, wait a few minutes and try again

## Troubleshooting
- **"API authentication failed"**: Check that your Client ID and Access Token are correct
- **"requests library not available"**: Install the requests library with `pip install requests`
- **"API connection error"**: Check your internet connection

## What the API Does
The IGDB API helps the tool match regional game name variants like:
- `Biohazard` ↔ `Resident Evil`
- `Pocket Monsters Blue` ↔ `Pokemon Blue`
- `Rockman` ↔ `Mega Man`

This allows the tool to properly group regional variants of the same game and remove duplicates while keeping your preferred region. 