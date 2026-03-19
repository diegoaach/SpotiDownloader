# SpotiDownloader - Project Context

## Pending Setup (user hasn't done this yet)
- [ ] Create Spotify Developer App — follow README Section 2 step-by-step


## What This Project Does
Python CLI script that authenticates with the Spotify Web API (OAuth2), fetches all tracks from a private playlist, then searches YouTube for each track and downloads it as MP3 via yt-dlp.

## Files
- `main.py` — Main script, all logic in one file
- `requirements.txt` — spotipy, yt-dlp, python-dotenv
- `.env.example` — Credentials template (commit this)
- `.env` — User's actual credentials (gitignored, never commit)
- `README.md` — Full setup instructions including Spotify app creation steps

## Key Implementation Details
- Auth: `SpotifyOAuth` from spotipy, scopes: `playlist-read-private playlist-read-collaborative`
- Token cached in `.cache` file (gitignored), auto-refreshed by spotipy
- Redirect URI: use `http://127.0.0.1:8888/callback` — Spotify dashboard rejects `localhost` but accepts the IP
- Pagination: uses `sp.next()` loop to handle playlists with >100 tracks
- Download: yt-dlp with `ytsearch1:` prefix, FFmpegExtractAudio postprocessor, 192 kbps MP3
- Output filename: `{Artist} - {Track}.mp3` via `safe_filename()` which strips illegal path characters
- Skip logic: checks if output file already exists before downloading (safe to re-run/resume)
- Retry logic: 3 attempts per track with varied search queries:
  1. `{name} {artist} audio`
  2. `{name} {artist} official audio`
  3. `{name} {artist}`
- Failed tracks written to `downloads/<playlist>/failed.txt`

## CLI Usage
```
python main.py --playlist <spotify_url_or_id> [--output ./downloads]
```

## Dependencies
- Python 3.10+
- FFmpeg (external, must be in PATH — required by yt-dlp for MP3 conversion)
- pip packages: spotipy, yt-dlp, python-dotenv

## Environment Variables (.env)
```
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```
