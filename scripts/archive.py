#!/usr/bin/env python3

"""
X Archive - archive.py v2.1

Production-oriented X/Twitter archive ingestion script.

Responsibilities
----------------
1. Validate incoming X posts using JSON Schema.
2. Deduplicate posts by X post ID.
3. Download image media.
4. Validate image MIME type and magic bytes.
5. Deduplicate media using SHA256.
6. Retry transient HTTP failures.
7. Handle HTTP 429 / Retry-After.
8. Atomically write media files.
9. Atomically update JSONL archive files.
10. Atomically update data/index.json.
11. Protect execution with an fcntl file lock.
12. Detect Git index.lock concurrency.
13. Detect NEW unsafe Git modifications introduced by this script.

Git responsibilities
--------------------
This script DOES NOT:
    - git add
    - git commit
    - git push
    - git pull
    - git reset
    - modify .gitignore
    - modify README.md
    - modify schema/
    - modify scripts/

Hermes should perform Git operations separately using:
    .locks/git.lock

Allowed archive output directories
----------------------------------
    data/
    archive/
    assets/

Pre-existing Git changes
------------------------
Pre-existing changes are allowed.

Example:

    ?? .gitignore
    ?? README.md
    ?? scripts/archive.v2.py

These are NOT treated as errors.

However, if archive.py itself creates/modifies:

    README.md
    schema/...
    scripts/...
    .gitignore

the Git safety guard will fail.

Version
-------
2.1.0
"""

from __future__ import annotations

import argparse
import contextlib
import fcntl
import hashlib
import json
import os
import sys
import tempfile
import time

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


# ============================================================================
# Optional dependency
# ============================================================================

try:
    from jsonschema import (
        Draft202012Validator,
        FormatChecker,
    )
except ImportError:
    print(
        "ERROR: jsonschema is not installed.",
        file=sys.stderr,
    )
    print(
        "Install with:",
        file=sys.stderr,
    )
    print(
        "    pip install jsonschema",
        file=sys.stderr,
    )
    sys.exit(1)


# ============================================================================
# Version
# ============================================================================

VERSION = "2.1.0"


# ============================================================================
# Repository paths
# ============================================================================

ROOT = Path(
    __file__
).resolve().parent.parent

SCHEMA_FILE = (
    ROOT
    / "schema"
    / "post.schema.json"
)

DATA_DIR = (
    ROOT
    / "data"
)

POSTS_DIR = (
    DATA_DIR
    / "posts"
)

INDEX_FILE = (
    DATA_DIR
    / "index.json"
)

ARCHIVE_DIR = (
    ROOT
    / "archive"
)

ASSETS_DIR = (
    ROOT
    / "assets"
)

IMAGE_DIR = (
    ASSETS_DIR
    / "images"
)

LOCK_DIR = (
    ROOT
    / ".locks"
)

ARCHIVE_LOCK_FILE = (
    LOCK_DIR
    / "archive.lock"
)

GIT_DIR = (
    ROOT
    / ".git"
)

GIT_INDEX_LOCK = (
    GIT_DIR
    / "index.lock"
)


# ============================================================================
# Runtime configuration
# ============================================================================

DEFAULT_TIMEOUT = 30

DEFAULT_RETRIES = 5

DEFAULT_BACKOFF = 2.0

DEFAULT_MAX_IMAGE_SIZE = (
    20 * 1024 * 1024
)

USER_AGENT = (
    "X-Archive/2.1 "
    "(archive ingestion agent)"
)

SUPPORTED_IMAGE_MIME = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
}

ALLOWED_GIT_PATHS = (
    "data/",
    "archive/",
    "assets/",
)


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

def log(
    message: str,
) -> None:

    timestamp = (
        datetime.now(
            timezone.utc
        )
        .strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    )

    print(
        f"[{timestamp}] {message}",
        flush=True,
    )


def log_warning(
    message: str,
) -> None:

    timestamp = (
        datetime.now(
            timezone.utc
        )
        .strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    )

    print(
        f"[{timestamp}] WARNING: {message}",
        file=sys.stderr,
        flush=True,
    )


def log_error(
    message: str,
) -> None:

    timestamp = (
        datetime.now(
            timezone.utc
        )
        .strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        )
    )

    print(
        f"[{timestamp}] ERROR: {message}",
        file=sys.stderr,
        flush=True,
    )


# ============================================================================
# Filesystem
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
                fcntl.LOCK_EX
                | fcntl.LOCK_NB,
            )

        except BlockingIOError:

            raise RuntimeError(
                "Another archive process "
                "is already running. "
                f"Lock: {ARCHIVE_LOCK_FILE}"
            )

        try:

            log(
                "Repository archive lock acquired."
            )

            yield

        finally:

            fcntl.flock(
                lock_file.fileno(),
                fcntl.LOCK_UN,
            )

            log(
                "Repository archive lock released."
            )


# ============================================================================
# Git
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
            "Another Git operation may be "
            f"running: {GIT_INDEX_LOCK}"
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
        for line
        in result.stdout.splitlines()
        if line.strip()
    ]


def git_path_from_status(
    line: str,
) -> str | None:

    if len(line) < 4:

        return None

    path = line[3:]

    # Handle rename:
    #
    # old/path -> new/path
    #
    if " -> " in path:

        path = (
            path
            .split(" -> ")[-1]
        )

    path = path.strip('"')

    return path


def is_allowed_git_path(
    path: str,
) -> bool:

    normalized = (
        path
        .replace("\\", "/")
    )

    return normalized.startswith(
        ALLOWED_GIT_PATHS
    )


def validate_git_changes(
    before: list[str],
    after: list[str],
) -> None:

    """
    Only NEW Git changes introduced by this
    archive operation are checked.

    Existing changes are intentionally ignored.
    """

    before_set = set(before)

    after_set = set(after)

    new_changes = (
        after_set
        - before_set
    )

    unexpected = []

    for status_line in new_changes:

        path = (
            git_path_from_status(
                status_line
            )
        )

        if path is None:

            continue

        if not is_allowed_git_path(
            path
        ):

            unexpected.append(
                status_line
            )

    if unexpected:

        raise RuntimeError(
            "Git safety guard detected "
            "NEW changes outside allowed "
            "directories "
            "(data/, archive/, assets/):\n"
            + "\n".join(
                unexpected
            )
        )


# ============================================================================
# JSON
# ============================================================================

def load_json(
    path: Path,
) -> Any:

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

    fd, temp_name = (
        tempfile.mkstemp(
            prefix=f".{path.name}.",
            suffix=".tmp",
            dir=str(
                path.parent
            ),
        )
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

            os.fsync(
                f.fileno()
            )

        os.replace(
            temp_name,
            path,
        )

    finally:

        if os.path.exists(
            temp_name
        ):

            os.unlink(
                temp_name
            )


def load_index() -> dict[str, Any]:

    if not INDEX_FILE.exists():

        return {}

    data = load_json(
        INDEX_FILE
    )

    if not isinstance(
        data,
        dict,
    ):

        raise RuntimeError(
            "data/index.json must "
            "contain a JSON object."
        )

    return data


# ============================================================================
# Schema validation
# ============================================================================

def load_validator():

    if not SCHEMA_FILE.exists():

        raise RuntimeError(
            f"Schema file not found: "
            f"{SCHEMA_FILE}"
        )

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
        validator.iter_errors(
            post
        ),
        key=lambda error:
        list(error.path),
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
            f"{location}: "
            f"{error.message}"
        )

    raise ValueError(
        "JSON Schema validation failed:\n"
        + "\n".join(
            messages
        )
    )


# ============================================================================
# Post normalization
# ============================================================================

def normalize_timestamp(
    value: str,
) -> str:

    dt = datetime.fromisoformat(
        value.replace(
            "Z",
            "+00:00",
        )
    )

    if dt.tzinfo is None:

        raise ValueError(
            "published_at must include "
            "a timezone."
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

    normalized = dict(
        post
    )

    normalized[
        "published_at"
    ] = normalize_timestamp(
        post["published_at"]
    )

    normalized[
        "content"
    ] = (
        post.get(
            "content"
        )
        or ""
    )

    return normalized


# ============================================================================
# SHA256
# ============================================================================

def sha256_bytes(
    data: bytes,
) -> str:

    return hashlib.sha256(
        data
    ).hexdigest()


def post_fingerprint(
    post: dict[str, Any],
) -> str:

    username = (
        post[
            "account"
        ][
            "username"
        ]
    )

    raw = (
        username
        + "\n"
        + post[
            "published_at"
        ]
        + "\n"
        + post[
            "content"
        ]
    )

    return sha256_bytes(
        raw.encode(
            "utf-8"
        )
    )


# ============================================================================
# Media validation
# ============================================================================

def detect_image_mime(
    data: bytes,
) -> str | None:

    # JPEG
    if data.startswith(
        b"\xff\xd8\xff"
    ):

        return "image/jpeg"

    # PNG
    if data.startswith(
        b"\x89PNG\r\n\x1a\n"
    ):

        return "image/png"

    # GIF
    if data.startswith(
        (
            b"GIF87a",
            b"GIF89a",
        )
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

    try:

        return mapping[mime]

    except KeyError:

        raise RuntimeError(
            f"Unsupported MIME: {mime}"
        )


# ============================================================================
# HTTP
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
    max_image_size: int,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> tuple[
    bytes,
    str,
]:

    last_error = None

    for attempt in range(
        retries + 1
    ):

        try:

            request = Request(
                url,
                headers={
                    "User-Agent":
                        USER_AGENT,

                    "Accept":
                        (
                            "image/avif,"
                            "image/webp,"
                            "image/apng,"
                            "image/*,"
                            "*/*;q=0.8"
                        ),
                },
            )

            with urlopen(
                request,
                timeout=timeout,
            ) as response:

                content_type = (
                    response.headers
                    .get(
                        "Content-Type",
                        "",
                    )
                    .split(
                        ";"
                    )[0]
                    .strip()
                    .lower()
                )

                content_length = (
                    response.headers
                    .get(
                        "Content-Length"
                    )
                )

                if content_length:

                    try:

                        if (
                            int(
                                content_length
                            )
                            > max_image_size
                        ):

                            raise RuntimeError(
                                "Image exceeds "
                                "maximum size of "
                                f"{max_image_size} "
                                "bytes."
                            )

                    except ValueError:

                        pass

                data = bytearray()

                while True:

                    chunk = (
                        response.read(
                            1024 * 1024
                        )
                    )

                    if not chunk:

                        break

                    data.extend(
                        chunk
                    )

                    if (
                        len(data)
                        > max_image_size
                    ):

                        raise RuntimeError(
                            "Image exceeded "
                            "maximum size of "
                            f"{max_image_size} "
                            "bytes."
                        )

                return (
                    bytes(data),
                    content_type,
                )

        except HTTPError as exc:

            last_error = exc

            status = exc.code

            retryable = (
                status == 429
                or 500 <= status <= 599
            )

            if not retryable:

                raise

            retry_after = (
                exc.headers.get(
                    "Retry-After"
                )
            )

            if (
                attempt
                >= retries
            ):

                raise

            delay = retry_delay(
                attempt + 1,
                retry_after,
            )

            log_warning(
                f"HTTP {status} "
                f"for media URL. "
                f"Retrying in "
                f"{delay:.1f}s "
                f"(attempt "
                f"{attempt + 1}/"
                f"{retries})."
            )

            time.sleep(
                delay
            )

        except (
            URLError,
            TimeoutError,
            ConnectionError,
        ) as exc:

            last_error = exc

            if (
                attempt
                >= retries
            ):

                raise

            delay = retry_delay(
                attempt + 1
            )

            log_warning(
                "Network error "
                "downloading media: "
                f"{exc}. "
                f"Retrying in "
                f"{delay:.1f}s "
                f"(attempt "
                f"{attempt + 1}/"
                f"{retries})."
            )

            time.sleep(
                delay
            )

    raise RuntimeError(
        "Download failed: "
        f"{last_error}"
    )


# ============================================================================
# Media index
# ============================================================================

def build_media_sha_index(
    index: dict[str, Any],
) -> dict[str, str]:

    result: dict[str, str] = {}

    for entry in index.values():

        media = entry.get(
            "media",
            [],
        )

        for item in media:

            sha = item.get(
                "sha256"
            )

            local_path = item.get(
                "local_path"
            )

            if sha and local_path:

                result.setdefault(
                    sha,
                    local_path,
                )

    return result


# ============================================================================
# Media download
# ============================================================================

def download_media(
    post: dict[str, Any],
    index: dict[str, Any],
    max_image_size: int,
    dry_run: bool = False,
) -> tuple[
    int,
    int,
    int,
]:

    downloaded = 0

    deduped = 0

    failed = 0

    media_list = post.get(
        "media",
        [],
    )

    if not media_list:

        return (
            0,
            0,
            0,
        )

    published = (
        datetime.fromisoformat(
            post[
                "published_at"
            ].replace(
                "Z",
                "+00:00",
            )
        )
        .astimezone(
            timezone.utc
        )
    )

    date_dir = (
        IMAGE_DIR
        / published.strftime(
            "%Y"
        )
        / published.strftime(
            "%m"
        )
        / published.strftime(
            "%d"
        )
    )

    if not dry_run:

        date_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    sha_index = (
        build_media_sha_index(
            index
        )
    )

    for (
        media_number,
        media,
    ) in enumerate(
        media_list,
        start=1,
    ):

        if (
            media.get("type")
            != "image"
        ):

            continue

        source_url = (
            media.get(
                "source_url"
            )
        )

        if not source_url:

            continue

        try:

            (
                data,
                server_mime,
            ) = download_bytes(
                source_url,
                max_image_size,
            )

            detected_mime = (
                detect_image_mime(
                    data[:64]
                )
            )

            if detected_mime is None:

                raise RuntimeError(
                    "Downloaded content "
                    "is not a recognized "
                    "image."
                )

            if (
                detected_mime
                not in SUPPORTED_IMAGE_MIME
            ):

                raise RuntimeError(
                    "Unsupported image MIME: "
                    f"{detected_mime}"
                )

            # Only reject an explicit image/*
            # mismatch. Some servers may omit
            # or incorrectly provide generic
            # application/octet-stream.
            if (
                server_mime
                and server_mime.startswith(
                    "image/"
                )
                and server_mime
                != detected_mime
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
            # SHA256 media dedup
            # ------------------------------------------------------------

            existing_path = (
                sha_index.get(
                    digest
                )
            )

            if existing_path:

                media[
                    "local_path"
                ] = existing_path

                media[
                    "sha256"
                ] = digest

                deduped += 1

                log(
                    "Media deduplicated: "
                    f"{post['id']} -> "
                    f"{existing_path}"
                )

                continue

            extension = (
                extension_for_mime(
                    detected_mime
                )
            )

            filename = (
                f"{post['id']}-"
                f"{media_number}"
                f"{extension}"
            )

            target = (
                date_dir
                / filename
            )

            relative_path = (
                target
                .relative_to(
                    ROOT
                )
                .as_posix()
            )

            if dry_run:

                log(
                    "[DRY-RUN] Would save "
                    f"{relative_path}"
                )

                media[
                    "local_path"
                ] = relative_path

                media[
                    "sha256"
                ] = digest

                downloaded += 1

                continue

            # ------------------------------------------------------------
            # Atomic media write
            # ------------------------------------------------------------

            fd, temp_name = (
                tempfile.mkstemp(
                    prefix=f".{filename}.",
                    suffix=".tmp",
                    dir=str(
                        date_dir
                    ),
                )
            )

            try:

                with os.fdopen(
                    fd,
                    "wb",
                ) as f:

                    f.write(
                        data
                    )

                    f.flush()

                    os.fsync(
                        f.fileno()
                    )

                os.replace(
                    temp_name,
                    target,
                )

            finally:

                if os.path.exists(
                    temp_name
                ):

                    os.unlink(
                        temp_name
                    )

            media[
                "local_path"
            ] = relative_path

            media[
                "sha256"
            ] = digest

            sha_index[
                digest
            ] = relative_path

            downloaded += 1

            log(
                "Downloaded image: "
                f"{relative_path} "
                f"({len(data)} bytes)"
            )

        except Exception as exc:

            failed += 1

            log_warning(
                "Media download failed "
                f"for post {post['id']}: "
                f"{source_url}: {exc}"
            )

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
# JSONL
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

        existing_data = (
            target.read_bytes()
        )

    new_line = (
        json.dumps(
            post,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
        )
        + "\n"
    ).encode(
        "utf-8"
    )

    combined = (
        existing_data
        + new_line
    )

    fd, temp_name = (
        tempfile.mkstemp(
            prefix=f".{target.name}.",
            suffix=".tmp",
            dir=str(
                target.parent
            ),
        )
    )

    try:

        with os.fdopen(
            fd,
            "wb",
        ) as f:

            f.write(
                combined
            )

            f.flush()

            os.fsync(
                f.fileno()
            )

        os.replace(
            temp_name,
            target,
        )

    finally:

        if os.path.exists(
            temp_name
        ):

            os.unlink(
                temp_name
            )


# ============================================================================
# Post archive location
# ============================================================================

def post_jsonl_path(
    post: dict[str, Any],
) -> Path:

    published = (
        datetime.fromisoformat(
            post[
                "published_at"
            ].replace(
                "Z",
                "+00:00",
            )
        )
        .astimezone(
            timezone.utc
        )
    )

    return (
        POSTS_DIR
        / published.strftime(
            "%Y"
        )
        / published.strftime(
            "%m"
        )
        / (
            published.strftime(
                "%Y-%m-%d"
            )
            + ".jsonl"
        )
    )


# ============================================================================
# Process post
# ============================================================================

def process_post(
    post: dict[str, Any],
    validator,
    index: dict[str, Any],
    max_image_size: int,
    dry_run: bool = False,
) -> ArchiveResult:

    post = normalize_post(
        post
    )

    validate_post(
        post,
        validator,
    )

    post_id = post[
        "id"
    ]

    # ------------------------------------------------------------
    # Post ID deduplication
    # ------------------------------------------------------------

    if post_id in index:

        log(
            "Duplicate post skipped: "
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
        max_image_size,
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
    # Build index entry
    # ------------------------------------------------------------

    published = (
        datetime.fromisoformat(
            post[
                "published_at"
            ].replace(
                "Z",
                "+00:00",
            )
        )
        .astimezone(
            timezone.utc
        )
    )

    index[post_id] = {
        "account": post[
            "account"
        ][
            "username"
        ],

        "date": published.strftime(
            "%Y-%m-%d"
        ),

        "file": (
            target
            .relative_to(
                ROOT
            )
            .as_posix()
        ),

        "fingerprint": (
            post_fingerprint(
                post
            )
        ),

        "media": [
            {
                "source_url":
                    item[
                        "source_url"
                    ],

                **(
                    {
                        "local_path":
                            item[
                                "local_path"
                            ]
                    }
                    if item.get(
                        "local_path"
                    )
                    else {}
                ),

                **(
                    {
                        "sha256":
                            item[
                                "sha256"
                            ]
                    }
                    if item.get(
                        "sha256"
                    )
                    else {}
                ),
            }

            for item in post.get(
                "media",
                []
            )

            if item.get(
                "type"
            ) == "image"
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
) -> list[
    dict[str, Any]
]:

    payload = load_json(
        path
    )

    if isinstance(
        payload,
        dict,
    ):

        return [
            payload
        ]

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
            "X Archive archive.py "
            f"v{VERSION}"
        )
    )

    parser.add_argument(
        "input",
        help=(
            "JSON file containing "
            "one or more X posts"
        ),
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Validate and simulate "
            "without modifying archive files"
        ),
    )

    parser.add_argument(
        "--max-image-size",
        type=int,
        default=DEFAULT_MAX_IMAGE_SIZE,
        help=(
            "Maximum image size in bytes "
            "(default: 20 MB)"
        ),
    )

    parser.add_argument(
        "--http-timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=(
            "HTTP timeout in seconds "
            "(default: 30)"
        ),
    )

    parser.add_argument(
        "--http-retries",
        type=int,
        default=DEFAULT_RETRIES,
        help=(
            "Maximum HTTP retries "
            "(default: 5)"
        ),
    )

    args = parser.parse_args()

    # ------------------------------------------------------------
    # Validate arguments
    # ------------------------------------------------------------

    if args.max_image_size <= 0:

        log_error(
            "--max-image-size must be > 0."
        )

        return EXIT_USAGE

    if args.http_timeout <= 0:

        log_error(
            "--http-timeout must be > 0."
        )

        return EXIT_USAGE

    if args.http_retries < 0:

        log_error(
            "--http-retries must be >= 0."
        )

        return EXIT_USAGE

    input_file = (
        Path(
            args.input
        )
        .resolve()
    )

    log(
        f"X Archive archive.py "
        f"v{VERSION}"
    )

    log(
        f"Repository: {ROOT}"
    )

    log(
        f"Input:      {input_file}"
    )

    log(
        f"Dry-run:    {args.dry_run}"
    )

    if not input_file.exists():

        log_error(
            "Input file not found: "
            f"{input_file}"
        )

        return EXIT_USAGE

    try:

        # --------------------------------------------------------
        # Repository validation
        # --------------------------------------------------------

        ensure_git_repository()

        check_git_index_lock()

        # --------------------------------------------------------
        # Acquire application lock FIRST.
        #
        # The Git baseline is intentionally captured AFTER
        # acquiring our lock, so two archive.py processes
        # cannot establish conflicting baselines.
        # --------------------------------------------------------

        with repository_lock():

            check_git_index_lock()

            before_git_status = (
                run_git_status_porcelain()
            )

            validator = (
                load_validator()
            )

            posts = (
                load_input_posts(
                    input_file
                )
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

            # ----------------------------------------------------
            # Load index
            # ----------------------------------------------------

            index = load_index()

            original_index = (
                json.loads(
                    json.dumps(
                        index
                    )
                )
            )

            new_count = 0

            duplicate_count = 0

            downloaded_count = 0

            deduped_media_count = 0

            failed_media_count = 0

            # ----------------------------------------------------
            # Process posts
            # ----------------------------------------------------

            for post in posts:

                if not isinstance(
                    post,
                    dict,
                ):

                    log_error(
                        "Each input post "
                        "must be a JSON object."
                    )

                    return EXIT_VALIDATION

                try:

                    result = (
                        process_post(
                            post,
                            validator,
                            index,
                            args.max_image_size,
                            dry_run=args.dry_run,
                        )
                    )

                except ValueError as exc:

                    log_error(
                        "Post validation "
                        f"failed: {exc}"
                    )

                    return EXIT_VALIDATION

                except Exception as exc:

                    log_error(
                        "Failed processing "
                        f"post "
                        f"{post.get('id', '<unknown>')}: "
                        f"{exc}"
                    )

                    return EXIT_INTERNAL

                if (
                    result.status
                    == "duplicate"
                ):

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

            # ----------------------------------------------------
            # Persist index ONLY when not dry-run
            # ----------------------------------------------------

            if not args.dry_run:

                save_json_atomic(
                    INDEX_FILE,
                    index,
                )

            else:

                # Explicitly restore in-memory index
                # so dry-run cannot accidentally persist
                # changes through future refactoring.
                index = (
                    original_index
                )

            # ----------------------------------------------------
            # Git safety verification
            # ----------------------------------------------------

            check_git_index_lock()

            after_git_status = (
                run_git_status_porcelain()
            )

            validate_git_changes(
                before_git_status,
                after_git_status,
            )

        # --------------------------------------------------------
        # Summary
        # --------------------------------------------------------

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
            f"Duplicates:         "
            f"{duplicate_count}"
        )

        print(
            f"Images downloaded:  "
            f"{downloaded_count}"
        )

        print(
            f"Media deduplicated: "
            f"{deduped_media_count}"
        )

        print(
            f"Image failures:     "
            f"{failed_media_count}"
        )

        print(
            f"Index entries:      "
            f"{len(index)}"
        )

        print(
            f"Dry run:            "
            f"{args.dry_run}"
        )

        print(
            "================================================"
        )

        # --------------------------------------------------------
        # Image failures do not fail the whole archive.
        #
        # The post remains archived and source_url remains
        # available for future media retry.
        # --------------------------------------------------------

        return EXIT_OK

    except RuntimeError as exc:

        message = str(
            exc
        )

        lower = (
            message.lower()
        )

        if (
            "another archive process"
            in lower
            or "archive lock"
            in lower
        ):

            log_error(
                message
            )

            return EXIT_LOCK

        if (
            "git"
            in lower
            or "repository"
            in lower
            or "index.lock"
            in lower
        ):

            log_error(
                message
            )

            return EXIT_GIT_SAFETY

        log_error(
            message
        )

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


# ============================================================================
# Entry point
# ============================================================================

if __name__ == "__main__":

    sys.exit(
        main()
    )
