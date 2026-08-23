#!/usr/bin/env python3

"""
X Archive - archive.py v2.0

Responsibilities:
    - Validate incoming X posts against JSON Schema
    - Deduplicate posts by X post ID
    - Deduplicate media by SHA256
    - Download images with retry/backoff
    - Handle HTTP 429 / 5xx responses
    - Validate image MIME type and magic bytes
    - Atomically update JSONL files
    - Atomically update data/index.json
    - Protect the repository with a file lock
    - Detect Git concurrency conditions
    - Prevent unexpected modifications outside:
        data/
        archive/
        assets/

This script intentionally DOES NOT perform git commit/push.
Hermes should perform Git operations after this script exits successfully.
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import mimetypes
import os
import shutil
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from jsonschema import Draft202012Validator, FormatChecker


# ============================================================================
# Version
# ============================================================================

VERSION = "2.0.0"


# ============================================================================
# Repository paths
# ============================================================================

ROOT = Path(__file__).resolve().parent.parent

SCHEMA_FILE = ROOT / "schema" / "post.schema.json"

DATA_DIR = ROOT / "data"
POSTS_DIR = DATA_DIR / "posts"
INDEX_FILE = DATA_DIR / "index.json"

ARCHIVE_DIR = ROOT / "archive"
ASSETS_DIR = ROOT / "assets"

IMAGE_DIR = ASSETS_DIR / "images"

LOCK_DIR = ROOT / ".locks"
ARCHIVE_LOCK_FILE = LOCK_DIR / "archive.lock"

GIT_DIR = ROOT / ".git"
GIT_INDEX_LOCK = GIT_DIR / "index.lock"


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_TIMEOUT = 30

DEFAULT_RETRIES = 5

DEFAULT_BACKOFF = 2.0

MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20 MB

MAX_REDIRECTS = 5

USER_AGENT = (
    "X-Archive/2.0 "
    "(https://github.com/YOUR_USERNAME/x-archive)"
)


ALLOWED_GIT_PATHS = (
    "data/",
    "archive/",
    "assets/",
)


SUPPORTED_IMAGE_MIME = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}


SUPPORTED_EXTENSIONS = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".gif": "image/gif",
}


# ============================================================================
# Exit codes
# ============================================================================

EXIT_OK = 0

EXIT_USAGE = 2

EXIT_VALIDATION = 10

EXIT_LOCK = 11

EXIT_GIT_SAFETY = 12

EXIT_NETWORK = 13

EXIT_MEDIA = 14

EXIT_INTERNAL = 20


# ============================================================================
# Data classes
# ============================================================================

@dataclass
class DownloadResult:
    success: bool
    local_path: str | None = None
    sha256: str | None = None
    bytes_downloaded: int = 0
    skipped: bool = False
    error: str | None = None


@dataclass
class ArchiveResult:
    status: str
    post_id: str
    downloaded: int = 0
    deduped_media: int = 0
    failed_media: int = 0


# ============================================================================
# Logging
# ============================================================================

def log(message: str) -> None:
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    print(f"[{timestamp}] {message}", flush=True)


def log_error(message: str) -> None:
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    print(
        f"[{timestamp}] ERROR: {message}",
        file=sys.stderr,
        flush=True,
    )


def log_warning(message: str) -> None:
    timestamp = datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )

    print(
        f"[{timestamp}] WARNING: {message}",
        file=sys.stderr,
        flush=True,
    )


# ============================================================================
# Filesystem helpers
# ============================================================================

def ensure_directories() -> None:

    LOCK_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    POSTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    ARCHIVE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    ASSETS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    IMAGE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


@contextlib.contextmanager
def repository_lock():

    ensure_directories()

    with ARCHIVE_LOCK_FILE.open(
        "w",
        encoding="utf-8",
    ) as lock_file:

        try:

            fcntl.flock(
                lock_file.fileno(),
                fcntl.LOCK_EX | fcntl.LOCK_NB,
            )

        except BlockingIOError:

            raise RuntimeError(
                "Another archive process is already running. "
                f"Lock: {ARCHIVE_LOCK_FILE}"
            )

        try:
            log("Repository archive lock acquired.")
            yield

        finally:

            fcntl.flock(
                lock_file.fileno(),
                fcntl.LOCK_UN,
            )

            log("Repository archive lock released.")


# ============================================================================
# Git safety
# ============================================================================

def ensure_git_repository() -> None:

    if not GIT_DIR.exists():

        raise RuntimeError(
            f"Not a Git repository: {ROOT}"
        )


def check_git_index_lock() -> None:

    if GIT_INDEX_LOCK.exists():

        raise RuntimeError(
            "Git index.lock exists. "
            "Another Git operation may be running: "
            f"{GIT_INDEX_LOCK}"
        )


def run_git_status_porcelain() -> list[str]:

    import subprocess

    result = subprocess.run(
        [
            "git",
            "-C",
            str(ROOT),
            "status",
            "--porcelain",
            "--untracked-files=all",
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:

        raise RuntimeError(
            "Unable to inspect Git status: "
            + result.stderr.strip()
        )

    return [
        line
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def git_path_from_status(line: str) -> str | None:

    if len(line) < 4:
        return None

    path = line[3:]

    # Handle renamed files:
    # old -> new
    if " -> " in path:
        path = path.split(" -> ")[-1]

    # Git quotes unusual filenames.
    path = path.strip('"')

    return path


def is_allowed_git_path(path: str) -> bool:

    normalized = path.replace("\\", "/")

    return normalized.startswith(
        ALLOWED_GIT_PATHS
    )


def validate_git_changes(
    before: list[str],
    after: list[str],
) -> None:

    before_set = set(before)
    after_set = set(after)

    new_changes = after_set - before_set

    unexpected = []

    for status_line in new_changes:

        path = git_path_from_status(status_line)

        if path is None:
            continue

        if not is_allowed_git_path(path):
            unexpected.append(
                f"{status_line}"
            )

    if unexpected:

        raise RuntimeError(
            "Git safety guard detected changes outside "
            "allowed directories "
            "(data/, archive/, assets/):\n"
            + "\n".join(unexpected)
        )


# ============================================================================
# JSON helpers
# ============================================================================

def load_json(path: Path) -> Any:

    with path.open(
        "r",
        encoding="utf-8",
    ) as f:

        return json.load(f)


def save_json_atomic(
    path: Path,
    data: Any,
) -> None:

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
    )

    try:

        with os.fdopen(
            fd,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )

            f.write("\n")

            f.flush()

            os.fsync(f.fileno())

        os.replace(
            temp_name,
            path,
        )

    finally:

        if os.path.exists(temp_name):
            os.unlink(temp_name)


def load_index() -> dict[str, Any]:

    if not INDEX_FILE.exists():
        return {}

    data = load_json(INDEX_FILE)

    if not isinstance(data, dict):

        raise RuntimeError(
            "data/index.json must contain a JSON object."
        )

    return data


# ============================================================================
# Schema validation
# ============================================================================

def load_validator():

    schema = load_json(
        SCHEMA_FILE
    )

    return Draft202012Validator(
        schema,
        format_checker=FormatChecker(),
    )


def validate_post(
    post: dict[str, Any],
    validator,
) -> None:

    errors = sorted(
        validator.iter_errors(post),
        key=lambda error: list(error.path),
    )

    if not errors:
        return

    messages = []

    for error in errors:

        location = ".".join(
            str(item)
            for item in error.path
        )

        if not location:
            location = "<root>"

        messages.append(
            f"{location}: {error.message}"
        )

    raise ValueError(
        "JSON Schema validation failed:\n"
        + "\n".join(messages)
    )


# ============================================================================
# Post normalization
# ============================================================================

def normalize_timestamp(value: str) -> str:

    dt = datetime.fromisoformat(
        value.replace(
            "Z",
            "+00:00",
        )
    )

    if dt.tzinfo is None:

        raise ValueError(
            "published_at must include timezone."
        )

    dt = dt.astimezone(
        timezone.utc
    )

    return dt.strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def normalize_post(
    post: dict[str, Any],
) -> dict[str, Any]:

    normalized = dict(post)

    normalized["published_at"] = normalize_timestamp(
        post["published_at"]
    )

    normalized["content"] = (
        post.get("content") or ""
    )

    return normalized


# ============================================================================
# Hash helpers
# ============================================================================

def sha256_bytes(data: bytes) -> str:

    return hashlib.sha256(
        data
    ).hexdigest()


def sha256_file(path: Path) -> str:

    digest = hashlib.sha256()

    with path.open("rb") as f:

        while True:

            chunk = f.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(chunk)

    return digest.hexdigest()


def post_fingerprint(
    post: dict[str, Any],
) -> str:

    raw = (
        post["account"]["username"]
        + "\n"
        + post["published_at"]
        + "\n"
        + post["content"]
    )

    return sha256_bytes(
        raw.encode("utf-8")
    )


# ============================================================================
# Media detection
# ============================================================================

def detect_image_mime(
    data: bytes,
) -> str | None:

    # JPEG
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"

    # PNG
    if data.startswith(
        b"\x89PNG\r\n\x1a\n"
    ):
        return "image/png"

    # GIF
    if data.startswith(
        (b"GIF87a", b"GIF89a")
    ):
        return "image/gif"

    # WEBP
    if (
        len(data) >= 12
        and data[:4] == b"RIFF"
        and data[8:12] == b"WEBP"
    ):
        return "image/webp"

    return None


def extension_for_mime(
    mime: str,
) -> str:

    mapping = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
    }

    return mapping[mime]


# ============================================================================
# HTTP download
# ============================================================================

def retry_delay(
    attempt: int,
    retry_after: str | None = None,
) -> float:

    if retry_after:

        try:
            seconds = float(
                retry_after
            )

            return min(
                seconds,
                300,
            )

        except ValueError:
            pass

    return min(
        DEFAULT_BACKOFF ** attempt,
        60,
    )


def download_bytes(
    url: str,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> tuple[bytes, str]:

    last_error = None

    for attempt in range(retries + 1):

        try:

            request = Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": (
                        "image/avif,image/webp,"
                        "image/apng,image/*,*/*;q=0.8"
                    ),
                },
            )

            with urlopen(
                request,
                timeout=timeout,
            ) as response:

                content_type = (
                    response.headers.get(
                        "Content-Type",
                        "",
                    )
                    .split(";")[0]
                    .strip()
                    .lower()
                )

                content_length = response.headers.get(
                    "Content-Length"
                )

                if content_length:

                    try:

                        if int(content_length) > MAX_IMAGE_SIZE:

                            raise RuntimeError(
                                "Image exceeds maximum "
                                f"size of {MAX_IMAGE_SIZE} bytes."
                            )

                    except ValueError:
                        pass

                data = bytearray()

                while True:

                    chunk = response.read(
                        1024 * 1024
                    )

                    if not chunk:
                        break

                    data.extend(chunk)

                    if len(data) > MAX_IMAGE_SIZE:

                        raise RuntimeError(
                            "Image exceeded maximum "
                            f"size of {MAX_IMAGE_SIZE} bytes."
                        )

                return bytes(data), content_type

        except HTTPError as exc:

            last_error = exc

            status = exc.code

            retryable = (
                status == 429
                or 500 <= status <= 599
            )

            if not retryable:
                raise

            retry_after = exc.headers.get(
                "Retry-After"
            )

            if attempt >= retries:
                raise

            delay = retry_delay(
                attempt + 1,
                retry_after,
            )

            log_warning(
                f"HTTP {status} for media URL. "
                f"Retrying in {delay:.1f}s "
                f"(attempt {attempt + 1}/{retries})."
            )

            time.sleep(delay)

        except (
            URLError,
            TimeoutError,
            ConnectionError,
        ) as exc:

            last_error = exc

            if attempt >= retries:
                raise

            delay = retry_delay(
                attempt + 1
            )

            log_warning(
                f"Network error downloading media: "
                f"{exc}. Retrying in "
                f"{delay:.1f}s "
                f"(attempt {attempt + 1}/{retries})."
            )

            time.sleep(delay)

    raise RuntimeError(
        f"Download failed: {last_error}"
    )


# ============================================================================
# Media index
# ============================================================================

def build_media_sha_index(
    index: dict[str, Any],
) -> dict[str, str]:

    result = {}

    for post_id, entry in index.items():

        media = entry.get(
            "media",
            [],
        )

        for item in media:

            sha = item.get(
                "sha256"
            )

            path = item.get(
                "local_path"
            )

            if sha and path:

                result.setdefault(
                    sha,
                    path,
                )

    return result


# ============================================================================
# Media download / deduplication
# ============================================================================

def download_media(
    post: dict[str, Any],
    index: dict[str, Any],
    dry_run: bool = False,
) -> tuple[int, int, int]:

    downloaded = 0
    deduped = 0
    failed = 0

    media_list = post.get(
        "media",
        [],
    )

    if not media_list:
        return 0, 0, 0

    published = datetime.fromisoformat(
        post["published_at"].replace(
            "Z",
            "+00:00",
        )
    ).astimezone(timezone.utc)

    date_dir = (
        IMAGE_DIR
        / published.strftime("%Y")
        / published.strftime("%m")
        / published.strftime("%d")
    )

    if not dry_run:

        date_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    sha_index = build_media_sha_index(
        index
    )

    for media_number, media in enumerate(
        media_list,
        start=1,
    ):

        if media.get("type") != "image":
            continue

        source_url = media.get(
            "source_url"
        )

        if not source_url:
            continue

        try:

            data, server_mime = download_bytes(
                source_url
            )

            detected_mime = detect_image_mime(
                data[:64]
            )

            if detected_mime is None:

                raise RuntimeError(
                    "Downloaded content is not "
                    "a recognized image."
                )

            if detected_mime not in SUPPORTED_IMAGE_MIME:

                raise RuntimeError(
                    f"Unsupported image MIME: "
                    f"{detected_mime}"
                )

            # If server declares a MIME type,
            # it must agree with detected content.
            if (
                server_mime
                and server_mime.startswith("image/")
                and server_mime != detected_mime
            ):

                raise RuntimeError(
                    "MIME mismatch: "
                    f"server={server_mime}, "
                    f"detected={detected_mime}"
                )

            digest = sha256_bytes(
                data
            )

            # ------------------------------------------------------------
            # Media SHA256 deduplication
            # ------------------------------------------------------------

            existing_path = sha_index.get(
                digest
            )

            if existing_path:

                media["local_path"] = (
                    existing_path
                )

                media["sha256"] = digest

                deduped += 1

                log(
                    f"Media deduplicated: "
                    f"{post['id']} -> "
                    f"{existing_path}"
                )

                continue

            extension = extension_for_mime(
                detected_mime
            )

            filename = (
                f"{post['id']}-"
                f"{media_number}"
                f"{extension}"
            )

            target = date_dir / filename

            relative_path = (
                target.relative_to(ROOT)
                .as_posix()
            )

            if dry_run:

                log(
                    f"[DRY-RUN] Would save "
                    f"{relative_path}"
                )

                media["local_path"] = (
                    relative_path
                )

                media["sha256"] = digest

                downloaded += 1

                continue

            # ------------------------------------------------------------
            # Atomic media write
            # ------------------------------------------------------------

            fd, temp_name = tempfile.mkstemp(
                prefix=f".{filename}.",
                suffix=".tmp",
                dir=str(date_dir),
            )

            try:

                with os.fdopen(
                    fd,
                    "wb",
                ) as f:

                    f.write(data)

                    f.flush()

                    os.fsync(f.fileno())

                os.replace(
                    temp_name,
                    target,
                )

            finally:

                if os.path.exists(temp_name):
                    os.unlink(temp_name)

            media["local_path"] = (
                relative_path
            )

            media["sha256"] = digest

            sha_index[digest] = (
                relative_path
            )

            downloaded += 1

            log(
                f"Downloaded image: "
                f"{relative_path} "
                f"({len(data)} bytes)"
            )

        except Exception as exc:

            failed += 1

            log_warning(
                f"Media download failed for "
                f"post {post['id']}: "
                f"{source_url}: {exc}"
            )

            # Do not remove source_url.
            # local_path is simply absent.
            media.pop(
                "local_path",
                None,
            )

            media.pop(
                "sha256",
                None,
            )

    return (
        downloaded,
        deduped,
        failed,
    )


# ============================================================================
# JSONL atomic update
# ============================================================================

def append_jsonl_atomic(
    target: Path,
    post: dict[str, Any],
) -> None:

    target.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    existing_data = b""

    if target.exists():

        existing_data = target.read_bytes()

    new_line = (
        json.dumps(
            post,
            ensure_ascii=False,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")

    combined = (
        existing_data
        + new_line
    )

    fd, temp_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=str(target.parent),
    )

    try:

        with os.fdopen(
            fd,
            "wb",
        ) as f:

            f.write(combined)

            f.flush()

            os.fsync(f.fileno())

        os.replace(
            temp_name,
            target,
        )

    finally:

        if os.path.exists(temp_name):
            os.unlink(temp_name)


# ============================================================================
# Post storage
# ============================================================================

def post_jsonl_path(
    post: dict[str, Any],
) -> Path:

    published = datetime.fromisoformat(
        post["published_at"].replace(
            "Z",
            "+00:00",
        )
    ).astimezone(timezone.utc)

    return (
        POSTS_DIR
        / published.strftime("%Y")
        / published.strftime("%m")
        / f"{published.strftime('%Y-%m-%d')}.jsonl"
    )


def process_post(
    post: dict[str, Any],
    validator,
    index: dict[str, Any],
    dry_run: bool = False,
) -> ArchiveResult:

    post = normalize_post(
        post
    )

    validate_post(
        post,
        validator,
    )

    post_id = post["id"]

    # ------------------------------------------------------------
    # Primary deduplication
    # ------------------------------------------------------------

    if post_id in index:

        log(
            f"Duplicate post skipped: "
            f"{post_id}"
        )

        return ArchiveResult(
            status="duplicate",
            post_id=post_id,
        )

    # ------------------------------------------------------------
    # Media
    # ------------------------------------------------------------

    (
        downloaded,
        deduped_media,
        failed_media,
    ) = download_media(
        post,
        index,
        dry_run=dry_run,
    )

    # ------------------------------------------------------------
    # JSONL
    # ------------------------------------------------------------

    target = post_jsonl_path(
        post
    )

    if not dry_run:

        append_jsonl_atomic(
            target,
            post,
        )

    # ------------------------------------------------------------
    # Index
    # ------------------------------------------------------------

    published = datetime.fromisoformat(
        post["published_at"].replace(
            "Z",
            "+00:00",
        )
    ).astimezone(timezone.utc)

    index[post_id] = {
        "account": post[
            "account"
        ]["username"],

        "date": published.strftime(
            "%Y-%m-%d"
        ),

        "file": target.relative_to(
            ROOT
        ).as_posix(),

        "fingerprint": post_fingerprint(
            post
        ),

        "media": [
            {
                "source_url": item[
                    "source_url"
                ],
                **(
                    {
                        "local_path": item[
                            "local_path"
                        ]
                    }
                    if item.get("local_path")
                    else {}
                ),
                **(
                    {
                        "sha256": item[
                            "sha256"
                        ]
                    }
                    if item.get("sha256")
                    else {}
                ),
            }
            for item in post.get(
                "media",
                []
            )
            if item.get("type") == "image"
        ],
    }

    return ArchiveResult(
        status="new",
        post_id=post_id,
        downloaded=downloaded,
        deduped_media=deduped_media,
        failed_media=failed_media,
    )


# ============================================================================
# Input
# ============================================================================

def load_input_posts(
    path: Path,
) -> list[dict[str, Any]]:

    payload = load_json(
        path
    )

    if isinstance(
        payload,
        dict,
    ):

        return [payload]

    if isinstance(
        payload,
        list,
    ):

        return payload

    raise ValueError(
        "Input JSON must contain "
        "an object or an array."
    )


# ============================================================================
# Main
# ============================================================================

def main() -> int:

    parser = argparse.ArgumentParser(
        description=(
            f"X Archive archive.py v{VERSION}"
        )
    )

    parser.add_argument(
        "input",
        help="JSON file containing one or more X posts",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and simulate without modifying files",
    )

    parser.add_argument(
        "--max-image-size",
        type=int,
        default=MAX_IMAGE_SIZE,
        help="Maximum image size in bytes",
    )

    args = parser.parse_args()
    max_image_size = args.max_image_size
    input_file = Path(
        args.input
    ).resolve()

    log(
        f"X Archive archive.py v{VERSION}"
    )

    log(
        f"Repository: {ROOT}"
    )

    if not input_file.exists():

        log_error(
            f"Input file not found: "
            f"{input_file}"
        )

        return EXIT_USAGE

    try:

        ensure_git_repository()

        check_git_index_lock()

        before_git_status = (
            run_git_status_porcelain()
        )

        # ------------------------------------------------------------
        # Safety check existing modifications
        # ------------------------------------------------------------

        unexpected_existing = []

        for line in before_git_status:

            path = git_path_from_status(
                line
            )

            if path is None:
                continue

            # Allow only our data directories.
            # Any existing modification outside them
            # causes a hard stop.
            if not is_allowed_git_path(path):

                unexpected_existing.append(
                    line
                )

        if unexpected_existing:

            raise RuntimeError(
                "Repository contains unexpected "
                "pre-existing Git changes outside "
                "data/, archive/, assets/:\n"
                + "\n".join(
                    unexpected_existing
                )
            )

        validator = load_validator()

        posts = load_input_posts(
            input_file
        )

        if not posts:

            log(
                "No posts supplied."
            )

            return EXIT_OK

        log(
            f"Posts discovered: "
            f"{len(posts)}"
        )

        with repository_lock():

            # Re-check Git concurrency after lock.
            check_git_index_lock()

            index = load_index()

            new_count = 0
            duplicate_count = 0
            downloaded_count = 0
            deduped_media_count = 0
            failed_media_count = 0

            for post in posts:

                try:

                    result = process_post(
                        post,
                        validator,
                        index,
                        dry_run=args.dry_run,
                    )

                except ValueError as exc:

                    log_error(
                        f"Post validation failed: "
                        f"{exc}"
                    )

                    return EXIT_VALIDATION

                except Exception as exc:

                    log_error(
                        f"Failed processing post "
                        f"{post.get('id', '<unknown>')}: "
                        f"{exc}"
                    )

                    return EXIT_INTERNAL

                if result.status == "duplicate":

                    duplicate_count += 1

                else:

                    new_count += 1

                downloaded_count += (
                    result.downloaded
                )

                deduped_media_count += (
                    result.deduped_media
                )

                failed_media_count += (
                    result.failed_media
                )

            # --------------------------------------------------------
            # Atomic index update
            # --------------------------------------------------------

            if not args.dry_run:

                save_json_atomic(
                    INDEX_FILE,
                    index,
                )

            # --------------------------------------------------------
            # Git safety validation
            # --------------------------------------------------------

            after_git_status = (
                run_git_status_porcelain()
            )

            validate_git_changes(
                before_git_status,
                after_git_status,
            )

        # ------------------------------------------------------------
        # Summary
        # ------------------------------------------------------------

        print()
        print(
            "================================================"
        )
        print(
            "X Archive Result"
        )
        print(
            "================================================"
        )

        print(
            f"Version:            {VERSION}"
        )

        print(
            f"Discovered:         {len(posts)}"
        )

        print(
            f"New:                {new_count}"
        )

        print(
            f"Duplicates:         {duplicate_count}"
        )

        print(
            f"Images downloaded:  {downloaded_count}"
        )

        print(
            f"Media deduplicated: {deduped_media_count}"
        )

        print(
            f"Image failures:     {failed_media_count}"
        )

        print(
            f"Index entries:      "
            f"{len(index)}"
        )

        print(
            f"Dry run:            {args.dry_run}"
        )

        print(
            "================================================"
        )

        # ------------------------------------------------------------
        # Important:
        #
        # Media failures do NOT fail the whole archive.
        #
        # The post and source_url are still preserved.
        # ------------------------------------------------------------

        return EXIT_OK

    except RuntimeError as exc:

        message = str(exc)

        if (
            "lock" in message.lower()
            or "already running" in message.lower()
        ):

            log_error(message)

            return EXIT_LOCK

        if (
            "Git" in message
            or "git" in message
            or "Repository" in message
        ):

            log_error(message)

            return EXIT_GIT_SAFETY

        log_error(message)

        return EXIT_INTERNAL

    except KeyboardInterrupt:

        log_error(
            "Interrupted by user."
        )

        return EXIT_INTERNAL

    except Exception as exc:

        log_error(
            f"Unexpected error: {exc}"
        )

        return EXIT_INTERNAL


if __name__ == "__main__":
    sys.exit(
        main()
    )
