"""
Google Drive client.

Auth setup (one-time):
  1. Go to console.cloud.google.com → APIs & Services → Credentials
  2. Create OAuth 2.0 Client ID (Desktop app)
  3. Download credentials.json → save to ~/.reorient/google_credentials.json
  4. Enable Drive API: console.cloud.google.com/apis/library/drive.googleapis.com
  5. Run: uv run python -c "from reorient.drive import auth; auth()"
     This opens a browser for one-time consent and saves a token.
"""

import os
import re
from pathlib import Path

from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/drive.activity.readonly",
]

_PRASS_DIR = Path.home() / ".reorient"
_TOKEN_PATH = _PRASS_DIR / "google_token.json"
_CREDS_PATH = Path(
    os.getenv("GOOGLE_CREDENTIALS_PATH", str(_PRASS_DIR / "google_credentials.json"))
)


def auth() -> Credentials:
    creds = None
    if _TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(_TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not _CREDS_PATH.exists():
                raise FileNotFoundError(
                    f"Google credentials not found at {_CREDS_PATH}.\n"
                    "See the auth setup instructions at the top of drive.py."
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(_CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        _PRASS_DIR.mkdir(parents=True, exist_ok=True)
        _TOKEN_PATH.write_text(creds.to_json())
    assert creds is not None
    return creds


def _drive():
    return build("drive", "v3", credentials=auth())


def recently_viewed(limit: int = 20) -> list[dict]:
    """Files recently opened by me, sorted by view time."""
    results = (
        _drive()
        .files()
        .list(
            pageSize=limit,
            orderBy="viewedByMeTime desc",
            q="viewedByMeTime > '2020-01-01T00:00:00' and trashed=false",
            fields="files(id,name,mimeType,viewedByMeTime,modifiedByMeTime,webViewLink)",
        )
        .execute()
    )
    return results.get("files", [])


def recently_edited(limit: int = 20) -> list[dict]:
    """Files I have modified recently."""
    results = (
        _drive()
        .files()
        .list(
            pageSize=limit,
            orderBy="modifiedByMeTime desc",
            q="trashed=false",
            fields="files(id,name,mimeType,modifiedByMeTime,webViewLink)",
        )
        .execute()
    )
    return results.get("files", [])


def unresolved_comments(file_id: str, my_email: str) -> list[dict]:
    """Unresolved comments on a file that mention my email."""
    try:
        results = (
            _drive()
            .comments()
            .list(
                fileId=file_id,
                includeDeleted=False,
                fields="comments(id,content,resolved,author,createdTime,replies)",
            )
            .execute()
        )
    except HttpError as e:
        if e.status_code == 403:
            return []  # no comment access on this file
        raise

    comments = results.get("comments", [])
    return [
        c
        for c in comments
        if not c.get("resolved", False) and my_email.lower() in c.get("content", "").lower()
    ]


def enrich_urls(urls: list[str]) -> list[dict]:
    """
    Given a list of drive.google.com URLs (e.g. extracted from Slack),
    return file metadata for each. Skips URLs that can't be resolved.
    """
    service = _drive()
    enriched = []
    for url in urls:
        file_id = _extract_file_id(url)
        if not file_id:
            continue
        try:
            file = (
                service.files()
                .get(
                    fileId=file_id,
                    fields="id,name,mimeType,modifiedByMeTime,viewedByMeTime,webViewLink",
                )
                .execute()
            )
            file["source_url"] = url
            enriched.append(file)
        except HttpError:
            continue
    return enriched


def _extract_file_id(url: str) -> str | None:
    patterns = [
        r"/d/([a-zA-Z0-9_-]+)",       # docs/sheets/slides
        r"[?&]id=([a-zA-Z0-9_-]+)",   # older drive URLs
        r"/folders/([a-zA-Z0-9_-]+)", # folders
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None
