from __future__ import annotations

from dataclasses import dataclass

from spotidownloader.utils import safe_filename as _safe_filename


@dataclass
class Track:
    name: str
    artist: str
    album: str

    @property
    def display_label(self) -> str:
        return f"{self.name} - {self.artist}"

    @property
    def safe_filename(self) -> str:
        return _safe_filename(f"{self.artist} - {self.name}.mp3")
