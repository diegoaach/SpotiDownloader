# SpotiDownloader - Project Context

## Pending Setup (user hasn't done this yet)
- [ ] Create Spotify Developer App — follow README Section 2 step-by-step


## What This Project Does
Python CLI script that authenticates with the Spotify Web API (OAuth2), fetches all tracks from a private playlist, then searches YouTube for each track and downloads it as MP3 via yt-dlp.

## Files
- `main.py` — CLI entry point, argument parsing, orchestration
- `spotidownloader/` — Package directory
  - `__init__.py` — Package exports
  - `models.py` — Track dataclass
  - `spotify.py` — Spotify API client
  - `downloader.py` — YouTube download logic (yt-dlp)
  - `utils.py` — safe_filename(), extract_playlist_id()
- `pyproject.toml` — Project metadata and dependencies (managed by uv)
- `.env` — User's actual credentials (gitignored, never commit)
- `README.md` — Full setup instructions including Spotify app creation steps

## Key Implementation Details
- Auth: `SpotifyOAuth` from spotipy, scopes: `playlist-read-private playlist-read-collaborative`
- Token cached in `.cache` file (gitignored), auto-refreshed by spotipy
- Redirect URI: use `http://127.0.0.1:8888/callback` — Spotify dashboard rejects `localhost` but accepts the IP
- Pagination: uses `sp.next()` loop to handle playlists with >100 tracks
- Download: yt-dlp searching YouTube Music (`music.youtube.com/search`), FFmpegExtractAudio postprocessor, 192 kbps MP3
- JS runtime: explicitly enables Node.js via `js_runtimes: {'node': {}, 'deno': {}}` (yt-dlp only enables Deno by default)
- Output filename: `{Artist} - {Track}.mp3` via `safe_filename()` which strips illegal path characters
- Skip logic: checks if output `.mp3` already exists before downloading (safe to re-run/resume)
- Retry logic: 3 attempts per track with varied search queries and exponential backoff (5s, 10s):
  1. `{name} {artist}`
  2. `{name} {artist} audio`
  3. `{name} {artist} official audio`
- Rate limiting: 5-10s random sleep between downloads to avoid YouTube throttling
- Instance rotation: YoutubeDL instance refreshed every 10 downloads to keep cookies/sessions fresh
- Failed tracks written to `downloads/<playlist>/failed.txt`

## CLI Usage
```
uv run python main.py --playlist <spotify_url_or_id> [--output ./downloads] [--browser opera]
```

## Package Manager
- This project uses **uv** — always use `uv run` to execute any Python scripts or commands (never bare `python`)
- Install/sync dependencies: `uv sync`
- Add a dependency: `uv add <package>`
- Dependencies are defined in `pyproject.toml`, pinned in `uv.lock`

## Dependencies
- Python 3.10+
- Node.js (external, must be in PATH — required by yt-dlp-ejs for YouTube JS challenge solving)
- FFmpeg (external, must be in PATH — required by yt-dlp for MP3 conversion)
- Python packages (in pyproject.toml): spotipy, yt-dlp, yt-dlp-ejs, python-dotenv

## Environment Variables (.env)
```
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

## Resolved Issue — YouTube JS Runtime (March 2026)
yt-dlp defaults to only enabling Deno as a JS runtime. Since Deno wasn't installed, no runtime was available for YouTube signature/n-challenge solving. Fixed by explicitly enabling Node.js via `'js_runtimes': {'node': {}, 'deno': {}}` in `downloader.py`.

**Important:** The browser used for cookie extraction (`--browser` flag) must be **closed** when running the tool, otherwise yt-dlp can't copy the cookie database (PermissionError).
