import argparse
import os
import re
import time

import yt_dlp
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

SPOTIFY_SCOPE = "playlist-read-private playlist-read-collaborative"
SEARCH_QUERIES = [
    "{name} {artist} audio",
    "{name} {artist} official audio",
    "{name} {artist}",
]


def get_spotify_client():
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

    if not client_id or not client_secret:
        raise SystemExit(
            "Missing Spotify credentials. Copy .env.example to .env and fill in your credentials."
        )

    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=SPOTIFY_SCOPE,
        )
    )


def extract_playlist_id(playlist_input):
    # Handle full URLs like https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=...
    match = re.search(r"playlist/([A-Za-z0-9]+)", playlist_input)
    if match:
        return match.group(1)
    # Assume it's already an ID
    return playlist_input


def get_all_tracks(sp, playlist_id):
    tracks = []
    results = sp.playlist_items(playlist_id, limit=100)
    while results:
        for item in results["items"]:
            track = item.get("track")
            if not track or track.get("is_local"):
                continue
            name = track["name"]
            artist = track["artists"][0]["name"] if track["artists"] else "Unknown"
            album = track["album"]["name"] if track.get("album") else ""
            tracks.append({"name": name, "artist": artist, "album": album})
        results = sp.next(results) if results.get("next") else None
    return tracks


def safe_filename(text):
    return re.sub(r'[<>:"/\\|?*]', "_", text)


def file_exists(output_dir, artist, name):
    filename = safe_filename(f"{artist} - {name}.mp3")
    return os.path.isfile(os.path.join(output_dir, filename))


def download_track(track, output_dir):
    name = track["name"]
    artist = track["artist"]
    album = track["album"]
    output_template = os.path.join(output_dir, safe_filename(f"{artist} - {name}") + ".%(ext)s")

    for attempt, query_template in enumerate(SEARCH_QUERIES, start=1):
        query = f"ytsearch1:{query_template.format(name=name, artist=artist)}"
        ydl_opts = {
            "format": "bestaudio/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
                {"key": "FFmpegMetadata"},
            ],
            "outtmpl": output_template,
            "quiet": True,
            "no_warnings": True,
            "postprocessor_args": [
                "-metadata", f"title={name}",
                "-metadata", f"artist={artist}",
                "-metadata", f"album={album}",
            ],
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([query])
            return True
        except Exception as e:
            if attempt < len(SEARCH_QUERIES):
                time.sleep(2)
            else:
                return False
    return False


def main():
    parser = argparse.ArgumentParser(description="Download a Spotify playlist as MP3s")
    parser.add_argument("--playlist", required=True, help="Spotify playlist URL or ID")
    parser.add_argument("--output", default="downloads", help="Output directory (default: downloads)")
    args = parser.parse_args()

    sp = get_spotify_client()
    playlist_id = extract_playlist_id(args.playlist)

    playlist = sp.playlist(playlist_id, fields="name")
    playlist_name = safe_filename(playlist["name"])
    output_dir = os.path.join(args.output, playlist_name)
    os.makedirs(output_dir, exist_ok=True)

    print(f"Playlist: {playlist['name']}")
    print(f"Output:   {output_dir}")
    print("Fetching tracks...")

    tracks = get_all_tracks(sp, playlist_id)
    total = len(tracks)
    print(f"Found {total} tracks.\n")

    failed = []

    for i, track in enumerate(tracks, start=1):
        name = track["name"]
        artist = track["artist"]
        label = f"{name} - {artist}"

        if file_exists(output_dir, artist, name):
            print(f"[{i}/{total}] Skipping (exists): {label}")
            continue

        print(f"[{i}/{total}] Downloading: {label}")
        success = download_track(track, output_dir)

        if not success:
            print(f"  [FAILED] {label}")
            failed.append(f"{artist} - {name}")

    if failed:
        failed_file = os.path.join(output_dir, "failed.txt")
        with open(failed_file, "w", encoding="utf-8") as f:
            f.write("\n".join(failed))
        print(f"\n{len(failed)} track(s) failed. See {failed_file}")
    else:
        print("\nAll tracks downloaded successfully.")


if __name__ == "__main__":
    main()
