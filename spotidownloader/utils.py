from __future__ import annotations

import re


def safe_filename(text: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', "_", text)


def extract_playlist_id(playlist_input: str) -> str:
    match = re.search(r"playlist/([A-Za-z0-9]+)", playlist_input)
    if match:
        return match.group(1)
    return playlist_input
