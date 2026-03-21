from __future__ import annotations

import os
import time
from typing import Any

import yt_dlp

from spotidownloader.models import Track
from spotidownloader.utils import safe_filename

_SEARCH_QUERIES: list[str] = [
    "{name} {artist} audio",
    "{name} {artist} official audio",
    "{name} {artist}",
]


class TrackDownloader:
    def __init__(self, output_dir: str, browser: str = "edge") -> None:
        self.output_dir: str = output_dir
        self.browser: str = browser

    def file_exists(self, track: Track) -> bool:
        return os.path.isfile(os.path.join(self.output_dir, track.safe_filename))

    def download(self, track: Track) -> bool:
        for attempt, query_template in enumerate(_SEARCH_QUERIES, start=1):
            query: str = f"ytsearch1:{query_template.format(name=track.name, artist=track.artist)}"
            ydl_opts: dict[str, Any] = self._build_ydl_opts(track)
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([query])
                return True
            except Exception as e:
                print(f"  [Attempt {attempt}] Error: {e}")
                if "Requested format" in str(e):
                    self._debug_formats(query)
                if attempt < len(_SEARCH_QUERIES):
                    time.sleep(2)
        return False

    def _debug_formats(self, query: str) -> None:
        try:
            opts: dict[str, Any] = {
                "cookiesfrombrowser": (self.browser,),
                "quiet": True,
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(query, download=False)
                print("  [DEBUG] Available formats:")
                for f in info.get("formats", []):
                    print(
                        f"    {f.get('format_id', '?'):>5}  "
                        f"{f.get('ext', '?'):>5}  "
                        f"acodec={f.get('acodec', 'none'):>10}  "
                        f"vcodec={f.get('vcodec', 'none'):>10}  "
                        f"{f.get('format_note', '')}"
                    )
        except Exception as dbg_err:
            print(f"  [DEBUG] Could not list formats: {dbg_err}")

    def _build_ydl_opts(self, track: Track) -> dict[str, Any]:
        output_template: str = os.path.join(
            self.output_dir,
            safe_filename(f"{track.artist} - {track.name}") + ".%(ext)s",
        )
        return {
            "format": "bestaudio*/best",
            "postprocessors": [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                },
                {"key": "FFmpegMetadata"},
            ],
            "outtmpl": output_template,
            "cookiesfrombrowser": (self.browser,),
            "verbose": True,
            "postprocessor_args": [
                "-metadata", f"title={track.name}",
                "-metadata", f"artist={track.artist}",
                "-metadata", f"album={track.album}",
            ],
        }
