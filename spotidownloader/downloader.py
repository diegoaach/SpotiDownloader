from __future__ import annotations

import os
import time
from typing import Any

import yt_dlp

from spotidownloader.models import Track
from spotidownloader.utils import safe_filename

_SEARCH_QUERIES: list[str] = [
    "{name} {artist}",
    "{name} {artist} audio",
    "{name} {artist} official audio",
]


class TrackDownloader:
    def __init__(self, output_dir: str, browser: str = "edge") -> None:
        self.output_dir: str = output_dir
        self.browser: str = browser

    def file_exists(self, track: Track) -> bool:
        return os.path.isfile(os.path.join(self.output_dir, track.safe_filename))

    def download(self, track: Track) -> bool:
        for attempt, query_template in enumerate(_SEARCH_QUERIES, start=1):
            search_term: str = query_template.format(name=track.name, artist=track.artist)
            query: str = f"https://music.youtube.com/search?q={search_term}"
            ydl_opts: dict[str, Any] = self._build_ydl_opts(track)
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([query])
                return True
            except Exception as e:
                print(f"  [Attempt {attempt}] Error: {e}")
                if attempt < len(_SEARCH_QUERIES):
                    time.sleep(2)
        return False

    def _build_ydl_opts(self, track: Track) -> dict[str, Any]:
        output_template: str = os.path.join(
            self.output_dir,
            safe_filename(f"{track.artist} - {track.name}") + ".%(ext)s",
        )
        return {
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
            "playlistend": 1,
            "cookiesfrombrowser": (self.browser,),
            "js_runtimes": {"node": {}, "deno": {}},
            "postprocessor_args": [
                "-metadata", f"title={track.name}",
                "-metadata", f"artist={track.artist}",
                "-metadata", f"album={track.album}",
            ],
        }
