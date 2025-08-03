# IGDB API Credentials

Some features of the ROM Collection Cleanup Tool use the [IGDB](https://api-docs.igdb.com/) database for improved name matching. You must supply your own credentials to enable these lookups.

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
You can supply the credentials in two ways:

* **Environment variables** – set them before running the program:
  ```bash
  export IGDB_CLIENT_ID="your-client-id"
  export IGDB_ACCESS_TOKEN="your-access-token"
  ```
* **GUI fields** – open `rom_cleanup_gui.py` and fill in the *IGDB Client ID* and *IGDB Access Token* inputs on the **Advanced** tab. The fields are prefilled from the environment variables if they are set.

The application only keeps the credentials in memory for the duration of the session. They are not written to disk.
