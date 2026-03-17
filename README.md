# SpotiDownloader

Download a private Spotify playlist as MP3 files. Authenticates with the Spotify Web API via OAuth2, fetches all tracks, then searches YouTube for each one and downloads it at 192 kbps with embedded metadata.

---

## Requirements

- Python 3.10+
- FFmpeg (required for MP3 conversion)

---

## 1. Install FFmpeg

**Windows (winget):**
```
winget install ffmpeg
```

**Windows (Chocolatey):**
```
choco install ffmpeg
```

**Manual:** Download from https://ffmpeg.org/download.html, extract, and add the `bin/` folder to your system PATH.

Verify it works:
```
ffmpeg -version
```

---

## 2. Create a Spotify App

You need a free Spotify Developer account to get API credentials.

### Step-by-step

1. Go to https://developer.spotify.com/dashboard and log in with your Spotify account.

2. Click **"Create app"**.

3. Fill in the form:
   - **App name**: anything (e.g. `SpotiDownloader`)
   - **App description**: anything
   - **Website**: leave blank
   - **Redirect URI**: `http://127.0.0.1:8888/callback`
     > Important: type this exactly. Use `127.0.0.1`, not `localhost` — Spotify's dashboard rejects the word `localhost` but accepts the IP address.
   - After typing the URI, click the **"Add"** button next to the field before saving, otherwise it won't be saved.

4. Under **"Which API/SDKs are you planning to use?"**, check **Web API**.

5. Check the terms of service box and click **Save**.

### Get your credentials

1. On your app's page, click **Settings**.
2. Copy the **Client ID**.
3. Click **"View client secret"** and copy the **Client Secret**.

---

## 3. Set Up the Project

**Clone or copy the project folder, then:**

```bash
# Install Python dependencies
pip install -r requirements.txt
```

Create a `.env` file by copying the example:

```bash
cp .env.example .env
```

Open `.env` and fill in your credentials:

```
SPOTIFY_CLIENT_ID=paste_your_client_id_here
SPOTIFY_CLIENT_SECRET=paste_your_client_secret_here
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

The redirect URI must match exactly what you entered in the Spotify dashboard.

---

## 4. Run

```bash
python main.py --playlist https://open.spotify.com/playlist/YOUR_PLAYLIST_ID
```

You can pass either a full Spotify URL or just the playlist ID.

**On first run:**
- A browser tab will open asking you to log in to Spotify and grant access.
- After granting access, you will be redirected to a `127.0.0.1` URL that fails to load — that is normal.
- Copy that full URL from the browser address bar and paste it into the terminal when prompted.
- The token is cached in a `.cache` file — subsequent runs skip the browser step.

**Optional flags:**
```bash
# Custom output directory (default: ./downloads)
python main.py --playlist <url> --output /path/to/music
```

---

## 5. Output

Tracks are saved to:
```
downloads/<playlist_name>/<Artist> - <Track>.mp3
```

- Already-downloaded tracks are skipped on re-runs (safe to resume).
- If any track fails after 3 attempts, it is listed in `downloads/<playlist_name>/failed.txt`.

---

## Troubleshooting

**"Missing Spotify credentials" error**
- Make sure `.env` exists and has the correct values (not the placeholder text from `.env.example`).

**Browser does not open / redirect fails**
- Make sure `http://127.0.0.1:8888/callback` is added in your Spotify app settings under Redirect URIs.
- Make sure the value in `.env` matches exactly.

**"FFmpeg not found" error**
- FFmpeg must be installed and available in your system PATH. Run `ffmpeg -version` to verify.

**Track downloads as `.webm` or wrong format**
- This means FFmpeg is missing. Install it and retry.

**Re-authenticating**
- Delete the `.cache` file and re-run to go through the browser login again.
