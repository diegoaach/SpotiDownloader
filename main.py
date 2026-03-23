from __future__ import annotations

import argparse
import os

from dotenv import load_dotenv

from spotidownloader import SpotifyClient, TrackDownloader
from spotidownloader.utils import extract_playlist_id, safe_filename

load_dotenv()


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Download a Spotify playlist as MP3s"
    )
    parser.add_argument("--playlist", required=True, help="Spotify playlist URL or ID")
    parser.add_argument("--output", default="downloads", help="Output directory (default: downloads)")
    parser.add_argument("--browser", default="edge", help="Browser to extract cookies from (default: edge)")
    args: argparse.Namespace = parser.parse_args()

    client: SpotifyClient = SpotifyClient()
    playlist_id: str = extract_playlist_id(args.playlist)

    playlist_name: str = client.get_playlist_name(playlist_id)
    output_dir: str = os.path.join(args.output, safe_filename(playlist_name))
    os.makedirs(output_dir, exist_ok=True)

    print(f"Playlist: {playlist_name}")
    print(f"Output:   {output_dir}")
    print("Fetching tracks...")

    tracks = client.get_all_tracks(playlist_id)
    total: int = len(tracks)
    print(f"Found {total} tracks.\n")

    downloader: TrackDownloader = TrackDownloader(output_dir, browser=args.browser)
    failed: list[str] = []

    try:
        for i, track in enumerate(tracks, start=1):
            if downloader.file_exists(track):
                print(f"[{i}/{total}] Skipping (exists): {track.display_label}")
                continue

            print(f"[{i}/{total}] Downloading: {track.display_label}")
            success: bool = downloader.download(track)

            if not success:
                print(f"  [FAILED] {track.display_label}")
                failed.append(f"{track.artist} - {track.name}")
    finally:
        downloader.close()

    if failed:
        failed_file: str = os.path.join(output_dir, "failed.txt")
        with open(failed_file, "w", encoding="utf-8") as f:
            f.write("\n".join(failed))
        print(f"\n{len(failed)} track(s) failed. See {failed_file}")
    else:
        print("\nAll tracks downloaded successfully.")


if __name__ == "__main__":
    main()
