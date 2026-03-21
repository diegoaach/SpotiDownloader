# SpotiDownloader - Project Context

## What This Project Does
Python CLI script that authenticates with the Spotify Web API (OAuth2), fetches all tracks from a private playlist, then searches YouTube for each track and downloads it as MP3 via yt-dlp.

## Files
- `main.py` — Main script, all logic in one file
- `requirements.txt` — spotipy, yt-dlp, yt-dlp-ejs, python-dotenv
- `.env.example` — Credentials template (commit this)
- `.env` — User's actual credentials (gitignored, never commit)
- `README.md` — Full setup instructions including Spotify app creation steps

## Key Implementation Details
- Auth: `SpotifyOAuth` from spotipy, scopes: `playlist-read-private playlist-read-collaborative`
- Token cached in `.cache` file (gitignored), auto-refreshed by spotipy
- Redirect URI: use `http://127.0.0.1:8888/callback` — Spotify dashboard rejects `localhost` but accepts the IP
- Pagination: uses `sp.next()` loop to handle playlists with >100 tracks
- Download: yt-dlp with `ytsearch1:` prefix, FFmpegExtractAudio postprocessor, 192 kbps MP3 (yt-dlp-ejs + Node.js for YouTube JS challenges)
- Output filename: `{Artist} - {Track}.mp3` via `safe_filename()` which strips illegal path characters
- Skip logic: checks if output file already exists before downloading (safe to re-run/resume)
- Retry logic: 3 attempts per track with varied search queries:
  1. `{name} {artist} audio`
  2. `{name} {artist} official audio`
  3. `{name} {artist}`
- Failed tracks written to `downloads/<playlist>/failed.txt`

## CLI Usage
```
python main.py --playlist <spotify_url_or_id> [--output ./downloads] [--browser opera]
```

## Dependencies
- Python 3.10+
- Node.js (external, must be in PATH — required by yt-dlp-ejs for YouTube JS challenge solving)
- FFmpeg (external, must be in PATH — required by yt-dlp for MP3 conversion)
- pip packages: spotipy, yt-dlp, yt-dlp-ejs, python-dotenv

## Environment Variables (.env)
```
SPOTIFY_CLIENT_ID=...
SPOTIFY_CLIENT_SECRET=...
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
```

## Current Issue — YouTube Download Broken (March 2026)

### What we tried
1. **pytubefix** — Failed with `get_initial_function_name: could not find match for multiple` (regex breakage from YouTube updating their player JS). The `sig-nsig` fix branch also didn't work.
2. **pytubefix with PO token** (`YouTube(url, client='WEB')`) — Same regex error, never gets to the download stage.
3. **yt-dlp + yt-dlp-ejs** — Current approach. Cookies from browser work (`Found YouTube account cookies`), but **JS runtimes are all showing as "unavailable"** even though Node.js v22.18.0 is installed on the system.

### Root cause (yt-dlp)
From verbose debug output:
```
[debug] [youtube] [jsc] JS Challenge Providers: bun (unavailable), deno (unavailable), node (unavailable), quickjs (unavailable)
WARNING: Signature solving failed
WARNING: n challenge solving failed
WARNING: Only images are available for download
```
- yt-dlp defaults to `'js_runtimes': {'deno': {}}` — only Deno enabled, not Node.js
- Even so, ALL runtimes show "unavailable", meaning yt-dlp-ejs can't find them
- Without a JS runtime, yt-dlp can't solve YouTube's signature/n-challenge, so no audio/video formats are extracted

### Next steps to try
1. **Check yt-dlp-ejs installation** — Run `python -c "import yt_dlp_ejs; print(yt_dlp_ejs.__version__)"` in the venv to confirm it's installed and what version
2. **Check node visibility from venv** — Run `where node` and verify it's in PATH when the venv is active
3. **Explicitly enable Node.js runtime** — Add `'js_runtimes': {'node': {}, 'deno': {}}` to `_build_ydl_opts` in `downloader.py`
4. **Try installing Deno** — yt-dlp recommends Deno as the default runtime: `winget install DenoLand.Deno`
5. **Check yt-dlp-ejs wiki** — https://github.com/yt-dlp/yt-dlp/wiki/EJS for setup requirements
6. **If all runtimes remain unavailable** — may need to reinstall yt-dlp-ejs or check if it requires a specific yt-dlp version

### Current state of the code
- `downloader.py` has **verbose logging ON** and **debug format listing** — remove both once downloads work
- `downloader.py` has `--browser` support (defaults to `edge`, user uses `opera`)
- Format selector is `bestaudio*/best`
- Error printing in retry loop is ON (temporary)
