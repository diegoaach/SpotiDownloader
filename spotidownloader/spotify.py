from __future__ import annotations

import os

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from spotidownloader.models import Track

_SPOTIFY_SCOPE: str = "playlist-read-private playlist-read-collaborative"


class SpotifyClient:
    def __init__(self) -> None:
        client_id: str | None = os.getenv("SPOTIFY_CLIENT_ID")
        client_secret: str | None = os.getenv("SPOTIFY_CLIENT_SECRET")
        redirect_uri: str = os.getenv("SPOTIFY_REDIRECT_URI", "http://127.0.0.1:8888/callback")

        if not client_id or not client_secret:
            raise SystemExit(
                "Missing Spotify credentials. Copy .env.example to .env and fill in your credentials."
            )

        self._sp: spotipy.Spotify = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope=_SPOTIFY_SCOPE,
            )
        )

    def get_playlist_name(self, playlist_id: str) -> str:
        playlist: dict = self._sp.playlist(playlist_id, fields="name")
        return playlist["name"]

    def get_all_tracks(self, playlist_id: str) -> list[Track]:
        tracks: list[Track] = []
        results: dict | None = self._sp.playlist_items(playlist_id, limit=100, market="from_token")
        while results:
            for item in results["items"]:
                raw: dict | None = item.get("track") or item.get("item")
                # print(f"DEBUG: item keys = {list(item.keys())}, track = {raw}")
                if not raw or raw.get("is_local"):
                    continue

                name: str = raw["name"]
                artist: str = raw["artists"][0]["name"] if raw["artists"] else "Unknown"
                album: str = raw["album"]["name"] if raw.get("album") else ""
                tracks.append(Track(name=name, artist=artist, album=album))
            results = self._sp.next(results) if results.get("next") else None
        return tracks
