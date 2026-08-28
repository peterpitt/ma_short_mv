#!/usr/bin/env python3
"""Upload an MP4 to YouTube using OAuth refresh-token or local browser auth.

CI requires YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, and
YOUTUBE_REFRESH_TOKEN. Local runs may use a cached authorized-user JSON token.
Never commit OAuth credentials or token files.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_URI = "https://oauth2.googleapis.com/token"
MAX_DOWNLOAD_BYTES = 512 * 1024 * 1024


class YouTubeUploader:
    def __init__(self, client_secret_file: str = "client_secret.json", token_file: str = ".youtube-token.json") -> None:
        self.client_secret_file = Path(client_secret_file)
        self.token_file = Path(token_file)
        self.youtube = None
        self.credentials: Credentials | None = None

    def _credentials_from_environment(self) -> Credentials | None:
        refresh_token = os.getenv("YOUTUBE_REFRESH_TOKEN")
        if not refresh_token:
            return None
        client_id = os.getenv("YOUTUBE_CLIENT_ID")
        client_secret = os.getenv("YOUTUBE_CLIENT_SECRET")
        missing = [
            name
            for name, value in (("YOUTUBE_CLIENT_ID", client_id), ("YOUTUBE_CLIENT_SECRET", client_secret))
            if not value
        ]
        if missing:
            raise RuntimeError("Missing required environment variables: " + ", ".join(missing))
        return Credentials(
            token=None,
            refresh_token=refresh_token,
            token_uri=TOKEN_URI,
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES,
        )

    def authenticate(self) -> None:
        """Use refresh-token auth in CI, or one-time browser auth locally."""
        credentials = self._credentials_from_environment()
        if credentials is not None:
            print("Using YouTube refresh-token authentication.")
            credentials.refresh(Request())
        elif self.token_file.exists():
            print(f"Loading cached OAuth token from {self.token_file}.")
            credentials = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
            if credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
        else:
            if not self.client_secret_file.exists():
                raise FileNotFoundError(
                    f"Client secret file not found: {self.client_secret_file}. "
                    "Download an OAuth desktop-app JSON file from Google Cloud Console."
                )
            print("Opening a browser for one-time local YouTube authorization.")
            flow = InstalledAppFlow.from_client_secrets_file(str(self.client_secret_file), SCOPES)
            credentials = flow.run_local_server(port=0, access_type="offline", prompt="consent")
            self.token_file.parent.mkdir(parents=True, exist_ok=True)
            self.token_file.write_text(credentials.to_json(), encoding="utf-8")
            print(f"Saved local OAuth token to {self.token_file}.")

        if not credentials or not credentials.valid:
            raise RuntimeError("YouTube authentication did not produce valid credentials.")
        self.credentials = credentials
        self.youtube = googleapiclient.discovery.build("youtube", "v3", credentials=credentials)

    @staticmethod
    def _parse_tags(tags: str) -> list[str]:
        return [tag.strip().lstrip("#") for tag in tags.split(",") if tag.strip()]

    @staticmethod
    def _validate_metadata(title: str, description: str, privacy_status: str) -> None:
        if not title.strip():
            raise ValueError("Video title cannot be empty.")
        if len(title) > 100:
            raise ValueError("Video title must be 100 characters or fewer.")
        if len(description) > 5000:
            raise ValueError("Video description must be 5,000 characters or fewer.")
        if privacy_status not in {"public", "unlisted", "private"}:
            raise ValueError("Privacy must be public, unlisted, or private.")

    @staticmethod
    def download_url(video_url: str) -> Path:
        if not video_url.startswith("https://"):
            raise ValueError("Video URL must use HTTPS.")
        temp = tempfile.NamedTemporaryFile(prefix="youtube-upload-", suffix=".mp4", delete=False)
        path = Path(temp.name)
        total = 0
        try:
            with urllib.request.urlopen(video_url, timeout=60) as response, temp:
                content_length = response.headers.get("Content-Length")
                if content_length and int(content_length) > MAX_DOWNLOAD_BYTES:
                    raise ValueError("Video URL points to a file larger than 512 MB.")
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > MAX_DOWNLOAD_BYTES:
                        raise ValueError("Video URL points to a file larger than 512 MB.")
                    temp.write(chunk)
        except Exception:
            path.unlink(missing_ok=True)
            raise
        print(f"Downloaded video ({total / (1024 * 1024):.1f} MB).")
        return path

    def _add_to_playlist(self, video_id: str, playlist_id: str) -> None:
        self.youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlist_id,
                    "resourceId": {"kind": "youtube#video", "videoId": video_id},
                }
            },
        ).execute()

    def upload_video(
        self,
        video_file: str,
        title: str,
        description: str = "",
        tags: str = "",
        playlist_id: str | None = None,
        privacy_status: str = "unlisted",
        category_id: str = "22",
        result_file: str | None = None,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        self._validate_metadata(title, description, privacy_status)
        path = Path(video_file).expanduser().resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Video file not found: {path}")
        if path.stat().st_size == 0:
            raise ValueError("Video file is empty.")
        if dry_run:
            result = {"dry_run": True, "title": title, "privacy_status": privacy_status}
            print("Dry run passed; no upload was performed.")
            if result_file:
                Path(result_file).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            return result
        if self.youtube is None:
            raise RuntimeError("Call authenticate() before upload_video().")

        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": self._parse_tags(tags),
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
                "selfDeclaredMadeForKids": False,
            },
        }
        request = self.youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=googleapiclient.http.MediaFileUpload(
                str(path), chunksize=1024 * 1024, resumable=True, mimetype="video/mp4"
            ),
        )
        response = None
        last_progress = -1
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    if progress != last_progress:
                        print(f"Upload progress: {progress}%")
                        last_progress = progress
            except googleapiclient.errors.HttpError:
                raise

        video_id = response["id"]
        if playlist_id:
            self._add_to_playlist(video_id, playlist_id)
        result = {
            "video_id": video_id,
            "video_url": f"https://www.youtube.com/watch?v={video_id}",
            "title": title,
            "privacy_status": privacy_status,
            "playlist_id": playlist_id,
        }
        if result_file:
            Path(result_file).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Upload succeeded: {result['video_url']}")
        return result

    def get_channel_info(self) -> dict[str, Any] | None:
        if self.youtube is None:
            raise RuntimeError("Call authenticate() before get_channel_info().")
        response = self.youtube.channels().list(part="snippet,statistics", mine=True).execute()
        if not response.get("items"):
            return None
        channel = response["items"][0]
        return {
            "id": channel["id"],
            "title": channel["snippet"].get("title", ""),
            "subscribers": channel.get("statistics", {}).get("subscriberCount", "N/A"),
            "videos": channel.get("statistics", {}).get("videoCount", "N/A"),
        }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Upload an animated short to YouTube.")
    parser.add_argument("video_file", nargs="?", help="Local MP4 path.")
    parser.add_argument("title", nargs="?", help="YouTube title.")
    parser.add_argument("--video-url", help="HTTPS URL to an MP4 file.")
    parser.add_argument("--description", default="", help="YouTube description.")
    parser.add_argument("--tags", default="", help="Comma-separated tags or hashtags.")
    parser.add_argument("--playlist-id", default=None, help="Optional playlist ID.")
    parser.add_argument("--privacy", choices=["public", "unlisted", "private"], default="unlisted")
    parser.add_argument("--category", default="22", help="YouTube category ID.")
    parser.add_argument("--client-secret", default="client_secret.json", help="OAuth client JSON path.")
    parser.add_argument("--token", default=".youtube-token.json", help="Local cached token JSON path.")
    parser.add_argument("--result-file", help="Write upload result JSON to this path.")
    parser.add_argument("--info", action="store_true", help="Print authenticated channel information.")
    parser.add_argument("--print-refresh-token", action="store_true", help="Print the refresh token for GitHub Actions setup.")
    parser.add_argument("--dry-run", action="store_true", help="Validate metadata and file without uploading.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.info or args.print_refresh_token:
        uploader = YouTubeUploader(args.client_secret, args.token)
        uploader.authenticate()
        if args.info:
            print(json.dumps(uploader.get_channel_info(), ensure_ascii=False, indent=2))
        if args.print_refresh_token:
            if not uploader.credentials or not uploader.credentials.refresh_token:
                raise RuntimeError("No refresh token was returned. Re-authorize locally with access_type=offline.")
            print(uploader.credentials.refresh_token)
        return 0
    if bool(args.video_file) == bool(args.video_url):
        print("Error: provide exactly one of a local video file or --video-url.", file=sys.stderr)
        return 2
    if not args.title:
        print("Error: provide a video title.", file=sys.stderr)
        return 2

    temporary_path: Path | None = None
    try:
        if args.video_url:
            temporary_path = YouTubeUploader.download_url(args.video_url)
            video_path = temporary_path
        else:
            video_path = Path(args.video_file)
        uploader = YouTubeUploader(args.client_secret, args.token)
        if not args.dry_run:
            uploader.authenticate()
        uploader.upload_video(
            str(video_path),
            args.title,
            args.description,
            args.tags,
            args.playlist_id,
            args.privacy,
            args.category,
            args.result_file,
            args.dry_run,
        )
        return 0
    except Exception as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    finally:
        if temporary_path:
            temporary_path.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
