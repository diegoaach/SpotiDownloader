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

_RETRY_BACKOFF: list[int] = [5, 10]
_INSTANCE_REFRESH_EVERY: int = 10


class TrackDownloader:
    def __init__(self, output_dir: str, browser: str = "edge") -> None:
        self.output_dir: str = output_dir
        self.browser: str = browser
        self._ydl: yt_dlp.YoutubeDL | None = None
        self._downloads_since_refresh: int = 0

    def file_exists(self, track: Track) -> bool:
        return os.path.isfile(os.path.join(self.output_dir, track.safe_filename))

    def close(self) -> None:
        if self._ydl is not None:
            self._ydl.__exit__(None, None, None)
            self._ydl = None

    def _get_ydl(self) -> yt_dlp.YoutubeDL:
        if self._ydl is None or self._downloads_since_refresh >= _INSTANCE_REFRESH_EVERY:
            self.close()
            self._ydl = yt_dlp.YoutubeDL(self._base_opts())
            self._ydl.__enter__()
            self._downloads_since_refresh = 0
        return self._ydl

    def download(self, track: Track) -> bool:
        ydl: yt_dlp.YoutubeDL = self._get_ydl()
        output_template: str = os.path.join(
            self.output_dir,
            safe_filename(f"{track.artist} - {track.name}") + ".%(ext)s",
        )
        ydl.params["outtmpl"] = {"default": output_template}
        ydl.params["postprocessor_args"] = [
            "-metadata", f"title={track.name}",
            "-metadata", f"artist={track.artist}",
            "-metadata", f"album={track.album}",
        ]

        for attempt, query_template in enumerate(_SEARCH_QUERIES, start=1):
            search_term: str = query_template.format(name=track.name, artist=track.artist)
            query: str = f"https://music.youtube.com/search?q={search_term}"
            try:
                ydl.download([query])
                self._downloads_since_refresh += 1
                return True
            except Exception as e:
                print(f"  [Attempt {attempt}] Error: {e}")
                if attempt < len(_SEARCH_QUERIES):
                    time.sleep(_RETRY_BACKOFF[attempt - 1])
        return False

    def _base_opts(self) -> dict[str, Any]:
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
            "quiet": True,
            "noprogress": False,
            "playlistend": 1,
            "cookiesfrombrowser": (self.browser,),
            "js_runtimes": {"node": {}, "deno": {}},
            "sleep_interval": 5,
            "max_sleep_interval": 10,
        }
