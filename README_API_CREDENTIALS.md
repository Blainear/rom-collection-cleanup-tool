# IGDB API credentials

Some features of the ROM Collection Cleanup Tool use the [IGDB](https://api-docs.igdb.com/) database for improved name matching. Users must supply their own credentials to enable these lookups.

## 1. Create a Twitch application
IGDB authentication is handled through Twitch. If you do not already have one, create a Twitch account and then visit the [Twitch Developer Console](https://dev.twitch.tv/console/apps) to create a new application. Note the **Client ID** that is generated.

## 2. Generate an access token
Use the Client ID along with your Twitch account to request an OAuth access token. The [IGDB authentication guide](https://api-docs.igdb.com/#authentication) describes several methods. A simple approach is to run:

```bash
curl -X POST 'https://id.twitch.tv/oauth2/token' \
 -H 'Content-Type: application/x-www-form-urlencoded' \
 -d 'client_id=YOUR_CLIENT_ID' \
 -d 'client_secret=YOUR_CLIENT_SECRET' \
 -d 'grant_type=client_credentials'
```

The response includes an `access_token` value.

## 3. Provide the credentials to the tool
Credentials can be supplied in two ways:

* **Environment variables** – set them before running the program:
 ```bash
 export IGDB_CLIENT_ID="your-client-id"
 export IGDB_ACCESS_TOKEN="your-access-token"
 ```
* **GUI fields** – open `rom_cleanup_gui.py` and fill in the IGDB Client ID and Access Token inputs on the Advanced tab. The fields are prefilled from the environment variables if they are set.

The application only keeps the credentials in memory for the duration of the session. They are not written to disk.

## Security notes
- API credentials are stored only in the GUI and are not saved to disk
- The credentials are used only for API calls to IGDB
- Credentials should not be shared publicly
- Access tokens can be regenerated from the IGDB dashboard if needed

## API usage limits
- IGDB provides free API access with defined rate limits
- The tool includes rate limiting to stay within these limits
- If rate limits are reached, wait before retrying

## Troubleshooting
- "API authentication failed": Check that the Client ID and Access Token are correct
- "requests library not available": Install the requests library with `pip install requests`
- "API connection error": Check the network connection

## What the API does
The IGDB API helps the tool match regional game name variants such as:
- `Biohazard` ↔ `Resident Evil`
- `Pocket Monsters Blue` ↔ `Pokemon Blue`
- `Rockman` ↔ `Mega Man`

This enables the tool to group regional variants of the same game and remove duplicates while keeping the preferred region.