#!/usr/bin/env python3
"""
X Archive EPUB Builder
======================

Build a production-ready EPUB 3 book from:

    archive/YYYY/MM/DD/*.md

Images are resolved from:

    assets/images/YYYY/MM/DD/

Image processing:
    - Maximum width: 1080px
    - JPEG quality: 78
    - Aspect ratio preserved
    - EXIF orientation corrected
    - PNG/WebP/etc. converted to JPEG
    - SHA256 deduplication
    - Source images are NEVER modified

Safety:
    - EPUB build fails if referenced images cannot be resolved.
    - EPUB output is written atomically.
    - Existing EPUB is not replaced if build fails.
    - Final EPUB ZIP structure is validated.

Usage:

    python scripts/build_epub.py 2026-08-24

Optional:

    python scripts/build_epub.py 2026-08-24 \
        --output epub/2026-08-24-x-archive.epub

Version:
    3.1.0
"""

from __future__ import annotations

import argparse
import hashlib
import html
import re
import sys
import tempfile
import unicodedata
import zipfile

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote

try:
    from PIL import Image, ImageOps
except ImportError:
    print("ERROR: Pillow is required.")
    print()
    print("Install with:")
    print("  pip install Pillow")
    sys.exit(1)


# ============================================================
# Configuration
# ============================================================

VERSION = "3.1.0"

MAX_IMAGE_WIDTH = 1080
JPEG_QUALITY = 78

REPOSITORY_IMAGE_ROOT = "assets/images"

BOOK_CSS = r"""
html {
    background: #ffffff;
}

body {
    margin: 0;
    padding: 0;
    background: #ffffff;
    color: #202124;
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        "Noto Sans",
        "Noto Sans CJK SC",
        Arial,
        sans-serif;
    font-size: 1em;
    line-height: 1.65;
}

main {
    max-width: 760px;
    margin: 0 auto;
    padding: 24px 20px 48px 20px;
}

h1 {
    font-size: 1.8em;
    line-height: 1.25;
    margin: 0 0 0.8em 0;
}

h2 {
    font-size: 1.4em;
    line-height: 1.3;
    margin-top: 2em;
}

h3 {
    font-size: 1.15em;
    margin-top: 1.6em;
}

p {
    margin: 0.7em 0;
}

.archive-post {
    margin: 0 0 2.2em 0;
    padding-bottom: 1.8em;
    border-bottom: 1px solid #dddddd;
    page-break-inside: avoid;
}

.post-meta {
    color: #666666;
    font-size: 0.88em;
    margin-bottom: 1em;
}

.post-account {
    font-weight: 600;
    color: #333333;
}

.post-content {
    font-size: 1.02em;
}

.post-content img {
    display: block;
    width: auto;
    max-width: 100%;
    height: auto;
    margin: 1.2em auto;
    border-radius: 6px;
}

.post-source {
    margin-top: 1em;
    font-size: 0.85em;
    word-break: break-word;
}

.post-source a {
    color: #1769aa;
    text-decoration: none;
}

.cover {
    text-align: center;
    padding-top: 25%;
}

.cover h1 {
    font-size: 2em;
}

.cover .subtitle {
    color: #666666;
    margin-top: 1em;
}

.toc {
    margin-top: 1em;
}

.toc a {
    text-decoration: none;
    color: #1769aa;
}

.small {
    color: #777777;
    font-size: 0.85em;
}

blockquote {
    margin: 1em 0;
    padding: 0.6em 1em;
    border-left: 4px solid #cccccc;
    color: #555555;
}

code {
    font-family: monospace;
    font-size: 0.9em;
}

ul,
ol {
    padding-left: 1.5em;
}

li {
    margin: 0.35em 0;
}
"""


# ============================================================
# Data classes
# ============================================================

@dataclass
class BookImage:
    source: Path
    epub_path: str
    width: int
    height: int
    sha256: str


@dataclass
class Post:
    account: str
    timestamp: str
    content: str
    source_url: str | None
    image_urls: list[str]
    source_file: Path


# ============================================================
# Logging
# ============================================================

def utc_now_string() -> str:
    return datetime.now(timezone.utc).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )


def log(message: str) -> None:
    print(
        f"[{utc_now_string()}] {message}",
        flush=True,
    )


# ============================================================
# Repository paths
# ============================================================

def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def images_root() -> Path:
    return repo_root() / REPOSITORY_IMAGE_ROOT


def output_directory() -> Path:
    directory = repo_root() / "epub"
    directory.mkdir(
        parents=True,
        exist_ok=True,
    )
    return directory


def archive_directory(date_value: str) -> Path:
    dt = validate_date(date_value)

    return (
        repo_root()
        / "archive"
        / f"{dt.year:04d}"
        / f"{dt.month:02d}"
        / f"{dt.day:02d}"
    )


# ============================================================
# CLI
# ============================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build an EPUB from an X Archive daily archive."
        )
    )

    parser.add_argument(
        "date",
        help="Archive date, e.g. 2026-08-24",
    )

    parser.add_argument(
        "--output",
        help="Optional output EPUB path.",
    )

    return parser.parse_args()


def validate_date(value: str) -> datetime:
    try:
        return datetime.strptime(
            value,
            "%Y-%m-%d",
        )
    except ValueError:
        raise SystemExit(
            f"ERROR: Invalid date '{value}'. "
            "Expected YYYY-MM-DD."
        )


# ============================================================
# Markdown parsing
# ============================================================

def parse_frontmatter(
    text: str,
) -> tuple[dict[str, str], str]:
    """
    Parse simple YAML-style frontmatter.

    Example:

    ---
    account: elonmusk
    time: 2026-08-24T04:20:25+00:00
    url: https://x.com/...
    ---
    """

    text = text.replace(
        "\r\n",
        "\n",
    )

    if not text.startswith("---"):
        return {}, text

    lines = text.split("\n")

    if len(lines) < 3:
        return {}, text

    if lines[0].strip() != "---":
        return {}, text

    end_index = None

    for i in range(1, len(lines)):
        if lines[i].strip() in (
            "---",
            "...",
        ):
            end_index = i
            break

    if end_index is None:
        return {}, text

    metadata: dict[str, str] = {}

    for line in lines[1:end_index]:

        match = re.match(
            r"^\s*([^:]+):\s*(.*)$",
            line,
        )

        if not match:
            continue

        key = match.group(1).strip()

        value = match.group(2).strip()

        value = (
            value
            .strip('"')
            .strip("'")
        )

        metadata[key] = value

    body = "\n".join(
        lines[end_index + 1:]
    )

    return metadata, body


def extract_account_from_filename(
    path: Path,
) -> str:
    return path.stem


def extract_account(
    text: str,
    path: Path,
) -> str:

    patterns = [
        r"(?:账号|account|username)\s*[:：]\s*([A-Za-z0-9_]{1,64})",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(1)

    return extract_account_from_filename(path)


def extract_timestamp(
    text: str,
) -> str:

    patterns = [
        r"(?:时间|time|timestamp)\s*[:：]\s*([0-9T:+\-\.Z]+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(1)

    return ""


def extract_source_url(
    text: str,
) -> str | None:

    patterns = [
        r"\[[^\]]*(?:原始链接|原文|source|original)[^\]]*\]"
        r"\((https?://[^)]+)\)",

        r"(?:原始链接|原文|source|original)"
        r"\s*[:：]\s*(https?://\S+)",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            re.IGNORECASE,
        )

        if match:
            return match.group(1).rstrip(
                ".,，。"
            )

    return None


def extract_images_from_markdown(
    text: str,
) -> list[str]:

    """
    Extract Markdown image references.

    Important:
        The path expression intentionally allows spaces.

    Example:

        ![image](path/to/file.jpg)

    """

    results: list[str] = []

    markdown_pattern = re.compile(
        r"!\[([^\]]*)\]\(([^)]+)\)"
    )

    html_pattern = re.compile(
        r'<img[^>]+src=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )

    for match in markdown_pattern.finditer(text):

        reference = match.group(2).strip()

        # Remove optional Markdown title.
        #
        # Example:
        # path/to/image.jpg "title"
        #
        title_match = re.match(
            r'^(.+?)\s+["\'][^"\']*["\']$',
            reference,
        )

        if title_match:
            reference = title_match.group(1).strip()

        results.append(reference)

    for match in html_pattern.finditer(text):

        results.append(
            match.group(1).strip()
        )

    unique: list[str] = []

    for item in results:

        if item not in unique:
            unique.append(item)

    return unique


def extract_content(
    text: str,
) -> str:

    lines = text.splitlines()

    output: list[str] = []

    metadata_prefixes = (
        "账号:",
        "账号：",
        "account:",
        "account：",

        "时间:",
        "时间：",
        "time:",
        "time：",

        "原始链接:",
        "原始链接：",
        "source:",
        "source：",

        "原文:",
        "原文：",
    )

    for line in lines:

        stripped = line.strip()

        if stripped == "---":
            continue

        if any(
            stripped.lower().startswith(
                prefix.lower()
            )
            for prefix in metadata_prefixes
        ):
            continue

        output.append(line)

    return "\n".join(
        output
    ).strip()


def load_posts(
    directory: Path,
) -> list[Post]:

    if not directory.exists():

        raise SystemExit(
            f"ERROR: Archive directory does not exist:\n"
            f"{directory}"
        )

    files = sorted(
        directory.glob("*.md")
    )

    if not files:

        raise SystemExit(
            f"ERROR: No Markdown files found:\n"
            f"{directory}"
        )

    posts: list[Post] = []

    for path in files:

        try:

            raw = path.read_text(
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            raise RuntimeError(
                f"Markdown file is not UTF-8: "
                f"{path}"
            )

        metadata, body = parse_frontmatter(
            raw
        )

        account = (
            metadata.get("account")
            or metadata.get("username")
            or extract_account(
                body,
                path,
            )
        )

        timestamp = (
            metadata.get("time")
            or metadata.get("timestamp")
            or extract_timestamp(
                body
            )
        )

        content = extract_content(
            body
        )

        source_url = (
            metadata.get("url")
            or metadata.get("source_url")
            or extract_source_url(
                body
            )
        )

        image_urls = (
            extract_images_from_markdown(
                body
            )
        )

        posts.append(
            Post(
                account=account,
                timestamp=timestamp,
                content=content,
                source_url=source_url,
                image_urls=image_urls,
                source_file=path,
            )
        )

    return posts


# ============================================================
# Image resolution
# ============================================================

def normalize_image_reference(
    image_ref: str,
) -> str:

    image_ref = image_ref.strip()

    # Remove query string.
    image_ref = image_ref.split(
        "?",
        1,
    )[0]

    # Remove fragment.
    image_ref = image_ref.split(
        "#",
        1,
    )[0]

    # URL decode.
    image_ref = unquote(
        image_ref
    )

    # Remove CR/LF/TAB.
    image_ref = (
        image_ref
        .replace("\r", "")
        .replace("\n", "")
        .replace("\t", "")
    )

    return image_ref.strip()


def is_remote_url(
    value: str,
) -> bool:

    return value.startswith(
        (
            "http://",
            "https://",
        )
    )


def resolve_local_image(
    image_ref: str,
    markdown_file: Path,
) -> Path | None:

    original_ref = image_ref

    image_ref = normalize_image_reference(
        image_ref
    )

    if not image_ref:
        return None

    if is_remote_url(image_ref):

        log(
            "WARNING: Remote image reference "
            "cannot be embedded because the "
            "source image was not downloaded locally: "
            f"{original_ref}"
        )

        return None

    root = repo_root()

    asset_root = images_root()

    candidates: list[Path] = []

    # --------------------------------------------------------
    # Candidate 1:
    # Relative to Markdown file.
    # --------------------------------------------------------

    if not image_ref.startswith("/"):

        candidates.append(
            markdown_file.parent
            / image_ref
        )

    # --------------------------------------------------------
    # Candidate 2:
    # Relative to repository root.
    # --------------------------------------------------------

    candidates.append(
        root
        / image_ref.lstrip("/")
    )

    # --------------------------------------------------------
    # Candidate 3:
    # Explicit assets/images path.
    # --------------------------------------------------------

    marker = (
        "assets/images/"
    )

    if marker in image_ref:

        relative = image_ref.split(
            marker,
            1,
        )[1]

        candidates.append(
            asset_root / relative
        )

    # --------------------------------------------------------
    # Direct candidate lookup.
    # --------------------------------------------------------

    checked: set[Path] = set()

    for candidate in candidates:

        try:

            resolved = candidate.resolve()

        except OSError:
            continue

        if resolved in checked:
            continue

        checked.add(resolved)

        if resolved.is_file():

            log(
                "INFO: Image resolved: "
                f"{original_ref} -> {resolved}"
            )

            return resolved

    # --------------------------------------------------------
    # Filename fallback.
    # --------------------------------------------------------

    filename = Path(
        image_ref
    ).name.strip()

    if not filename:
        return None

    matches = list(
        asset_root.rglob(
            filename
        )
    )

    if len(matches) == 1:

        resolved = matches[0].resolve()

        log(
            "INFO: Image resolved by "
            "filename fallback: "
            f"{original_ref} -> {resolved}"
        )

        return resolved

    if len(matches) > 1:

        log(
            "ERROR: Multiple images match "
            f"filename '{filename}'."
        )

        for match in matches[:10]:
            log(
                f"ERROR: Candidate: {match}"
            )

        return None

    # --------------------------------------------------------
    # Filename whitespace normalization.
    #
    # Example:
    #
    # 209173186505 3139179-1.jpg
    #
    # becomes:
    #
    # 2091731865053139179-1.jpg
    # --------------------------------------------------------

    compact_filename = re.sub(
        r"\s+",
        "",
        filename,
    )

    if compact_filename != filename:

        matches = list(
            asset_root.rglob(
                compact_filename
            )
        )

        if len(matches) == 1:

            resolved = matches[0].resolve()

            log(
                "INFO: Image resolved after "
                "whitespace normalization: "
                f"{original_ref} -> {resolved}"
            )

            return resolved

        if len(matches) > 1:

            log(
                "ERROR: Multiple images match "
                f"normalized filename "
                f"'{compact_filename}'."
            )

            return None

    return None


# ============================================================
# Image processing
# ============================================================

def sha256_file(
    path: Path,
) -> str:

    digest = hashlib.sha256()

    with path.open(
        "rb"
    ) as handle:

        while True:

            chunk = handle.read(
                1024 * 1024
            )

            if not chunk:
                break

            digest.update(
                chunk
            )

    return digest.hexdigest()


def prepare_image(
    source: Path,
    output_path: Path,
) -> tuple[int, int, str]:

    """
    Convert source image to optimized JPEG.

    Rules:
        width <= 1080px
        JPEG quality = 78
    """

    with Image.open(
        source
    ) as original:

        image = ImageOps.exif_transpose(
            original
        )

        width, height = image.size

        if width > MAX_IMAGE_WIDTH:

            new_height = round(
                height
                * MAX_IMAGE_WIDTH
                / width
            )

            image = image.resize(
                (
                    MAX_IMAGE_WIDTH,
                    new_height,
                ),
                Image.Resampling.LANCZOS,
            )

        if image.mode in (
            "RGBA",
            "LA",
        ):

            background = Image.new(
                "RGB",
                image.size,
                "white",
            )

            alpha = image.getchannel(
                "A"
            )

            background.paste(
                image,
                mask=alpha,
            )

            image = background

        elif image.mode != "RGB":

            image = image.convert(
                "RGB"
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        image.save(
            output_path,
            format="JPEG",
            quality=JPEG_QUALITY,
            optimize=True,
            progressive=True,
        )

        final_width, final_height = (
            image.size
        )

    digest = sha256_file(
        output_path
    )

    return (
        final_width,
        final_height,
        digest,
    )


def build_image_assets(
    posts: Iterable[Post],
    temp_dir: Path,
) -> tuple[
    dict[str, BookImage],
    int,
    int,
    int,
    int,
]:
    """
    Resolve and process images.

    Returns:

        image_map
        processed_count
        deduplicated_count
        reference_count
        failure_count
    """

    image_map: dict[
        str,
        BookImage,
    ] = {}

    digest_to_epub: dict[
        str,
        str,
    ] = {}

    reference_count = 0
    processed_count = 0
    deduplicated_count = 0
    failure_count = 0

    image_counter = 0

    for post in posts:

        for image_ref in post.image_urls:

            reference_count += 1

            if image_ref in image_map:
                continue

            source = resolve_local_image(
                image_ref,
                post.source_file,
            )

            if source is None:

                failure_count += 1

                log(
                    "ERROR: Image resolution failed: "
                    f"{image_ref}"
                )

                log(
                    "ERROR: Referenced by: "
                    f"{post.source_file}"
                )

                continue

            image_counter += 1

            temporary_name = (
                f"image-{image_counter:05d}.jpg"
            )

            temp_output = (
                temp_dir
                / temporary_name
            )

            try:

                width, height, digest = (
                    prepare_image(
                        source,
                        temp_output,
                    )
                )

            except Exception as exc:

                failure_count += 1

                log(
                    "ERROR: Cannot process image "
                    f"{source}: {exc}"
                )

                continue

            # ------------------------------------------------
            # SHA256 deduplication.
            # ------------------------------------------------

            if digest in digest_to_epub:

                epub_path = (
                    digest_to_epub[
                        digest
                    ]
                )

                deduplicated_count += 1

                image_map[
                    image_ref
                ] = BookImage(
                    source=source,
                    epub_path=epub_path,
                    width=width,
                    height=height,
                    sha256=digest,
                )

                continue

            epub_filename = (
                f"{digest[:16]}.jpg"
            )

            epub_path = (
                f"OEBPS/images/"
                f"{epub_filename}"
            )

            digest_to_epub[
                digest
            ] = epub_path

            image_map[
                image_ref
            ] = BookImage(
                source=source,
                epub_path=epub_path,
                width=width,
                height=height,
                sha256=digest,
            )

            processed_count += 1

    return (
        image_map,
        processed_count,
        deduplicated_count,
        reference_count,
        failure_count,
    )


# ============================================================
# HTML / Markdown
# ============================================================

def escape_text(
    value: str,
) -> str:

    return html.escape(
        value,
        quote=True,
    )


def markdown_to_html(
    text: str,
    image_map: dict[str, BookImage],
) -> str:

    lines = text.splitlines()

    result: list[str] = []

    in_ul = False
    in_ol = False
    in_blockquote = False
    in_code = False

    paragraph: list[str] = []

    def close_lists() -> None:

        nonlocal in_ul, in_ol

        if in_ul:

            result.append(
                "</ul>"
            )

            in_ul = False

        if in_ol:

            result.append(
                "</ol>"
            )

            in_ol = False

    def flush_paragraph() -> None:

        nonlocal paragraph

        if paragraph:

            text_value = " ".join(
                item.strip()
                for item in paragraph
            )

            result.append(
                "<p>"
                + inline_markdown(
                    text_value,
                    image_map,
                )
                + "</p>"
            )

            paragraph = []

    for line in lines:

        stripped = line.strip()

        if stripped.startswith("```"):

            flush_paragraph()
            close_lists()

            if in_code:

                result.append(
                    "</code></pre>"
                )

                in_code = False

            else:

                result.append(
                    "<pre><code>"
                )

                in_code = True

            continue

        if in_code:

            result.append(
                escape_text(line)
            )

            continue

        if not stripped:

            flush_paragraph()

            if in_blockquote:

                result.append(
                    "</blockquote>"
                )

                in_blockquote = False

            continue

        heading = re.match(
            r"^(#{1,3})\s+(.+)$",
            stripped,
        )

        if heading:

            flush_paragraph()
            close_lists()

            level = len(
                heading.group(1)
            )

            content = inline_markdown(
                heading.group(2),
                image_map,
            )

            result.append(
                f"<h{level}>"
                f"{content}"
                f"</h{level}>"
            )

            continue

        if stripped.startswith(">"):

            flush_paragraph()
            close_lists()

            if not in_blockquote:

                result.append(
                    "<blockquote>"
                )

                in_blockquote = True

            quote_text = (
                stripped[1:].strip()
            )

            result.append(
                "<p>"
                + inline_markdown(
                    quote_text,
                    image_map,
                )
                + "</p>"
            )

            continue

        ul = re.match(
            r"^[-*+]\s+(.+)$",
            stripped,
        )

        if ul:

            flush_paragraph()

            if in_ol:

                result.append(
                    "</ol>"
                )

                in_ol = False

            if not in_ul:

                result.append(
                    "<ul>"
                )

                in_ul = True

            result.append(
                "<li>"
                + inline_markdown(
                    ul.group(1),
                    image_map,
                )
                + "</li>"
            )

            continue

        ol = re.match(
            r"^\d+\.\s+(.+)$",
            stripped,
        )

        if ol:

            flush_paragraph()

            if in_ul:

                result.append(
                    "</ul>"
                )

                in_ul = False

            if not in_ol:

                result.append(
                    "<ol>"
                )

                in_ol = True

            result.append(
                "<li>"
                + inline_markdown(
                    ol.group(1),
                    image_map,
                )
                + "</li>"
            )

            continue

        close_lists()

        if in_blockquote:

            result.append(
                "</blockquote>"
            )

            in_blockquote = False

        paragraph.append(
            stripped
        )

    flush_paragraph()
    close_lists()

    if in_blockquote:

        result.append(
            "</blockquote>"
        )

    if in_code:

        result.append(
            "</code></pre>"
        )

    return "\n".join(
        result
    )


def inline_markdown(
    text: str,
    image_map: dict[str, BookImage],
) -> str:

    placeholders: dict[
        str,
        str,
    ] = {}

    counter = 0

    image_pattern = re.compile(
        r"!\[([^\]]*)\]\(([^)]+)\)"
    )

    def replace_image(
        match: re.Match,
    ) -> str:

        nonlocal counter

        alt = match.group(1)

        ref = match.group(2).strip()

        title_match = re.match(
            r'^(.+?)\s+["\'][^"\']*["\']$',
            ref,
        )

        if title_match:

            ref = (
                title_match.group(1)
                .strip()
            )

        image = image_map.get(
            ref
        )

        if image is None:

            # This should normally never happen
            # because build_image_assets()
            # already validates every image.
            raise RuntimeError(
                "Internal error: image "
                "reference has no "
                f"resolved mapping: {ref}"
            )

        counter += 1

        token = (
            f"___XARCHIVE_IMAGE_{counter}___"
        )

        relative_image = (
            "../images/"
            + Path(
                image.epub_path
            ).name
        )

        img_html = (
            f'<img src="'
            f'{escape_text(relative_image)}" '
            f'alt="'
            f'{escape_text(alt or "image")}" '
            f'width="'
            f'{image.width}" '
            f'height="'
            f'{image.height}" />'
        )

        placeholders[
            token
        ] = img_html

        return token

    text = image_pattern.sub(
        replace_image,
        text,
    )

    escaped = html.escape(
        text,
        quote=False,
    )

    escaped = re.sub(
        r"\[([^\]]+)\]"
        r"\((https?://[^)]+)\)",
        r'<a href="\2">\1</a>',
        escaped,
    )

    escaped = re.sub(
        r"\*\*(.+?)\*\*",
        r"<strong>\1</strong>",
        escaped,
    )

    escaped = re.sub(
        r"__(.+?)__",
        r"<strong>\1</strong>",
        escaped,
    )

    escaped = re.sub(
        r"\*([^*]+?)\*",
        r"<em>\1</em>",
        escaped,
    )

    escaped = re.sub(
        r"_([^_]+?)_",
        r"<em>\1</em>",
        escaped,
    )

    escaped = escaped.replace(
        "  \n",
        "<br />",
    )

    for token, replacement in (
        placeholders.items()
    ):

        escaped = escaped.replace(
            token,
            replacement,
        )

    return escaped


# ============================================================
# XHTML generation
# ============================================================

def create_cover_xhtml(
    date_value: str,
    post_count: int,
) -> str:

    title = (
        f"X Archive — {date_value}"
    )

    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops">
<head>
<meta charset="utf-8"/>
<title>{escape_text(title)}</title>
<link rel="stylesheet" type="text/css"
      href="styles/style.css"/>
</head>
<body>
<main class="cover">
<h1>{escape_text(title)}</h1>
<p class="subtitle">
{post_count} archived posts
</p>
<p class="small">
Generated by X Archive
</p>
</main>
</body>
</html>
"""


def post_html(
    post: Post,
    index: int,
    image_map: dict[str, BookImage],
) -> str:

    if post.timestamp:

        title = (
            f"{post.account} — "
            f"{post.timestamp}"
        )

    else:

        title = post.account

    content_html = markdown_to_html(
        post.content,
        image_map,
    )

    source_html = ""

    if post.source_url:

        source_html = (
            '<p class="post-source">'
            '<a href="'
            f"{escape_text(post.source_url)}"
            '">Original post</a>'
            "</p>"
        )

    return f"""
<article class="archive-post"
         id="post-{index}">
<h2>{escape_text(title)}</h2>

<div class="post-meta">
<span class="post-account">
@{escape_text(post.account)}
</span>
</div>

<div class="post-content">
{content_html}
</div>

{source_html}

</article>
"""


def create_posts_xhtml(
    date_value: str,
    posts: list[Post],
    image_map: dict[str, BookImage],
) -> str:

    title = (
        f"X Archive — {date_value}"
    )

    articles = []

    for index, post in enumerate(
        posts,
        start=1,
    ):

        articles.append(
            post_html(
                post,
                index,
                image_map,
            )
        )

    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops">
<head>
<meta charset="utf-8"/>
<title>{escape_text(title)}</title>
<link rel="stylesheet" type="text/css"
      href="styles/style.css"/>
</head>
<body>
<main>
<h1>{escape_text(title)}</h1>
{''.join(articles)}
</main>
</body>
</html>
"""


def create_toc_xhtml(
    date_value: str,
    posts: list[Post],
) -> str:

    title = (
        f"Contents — {date_value}"
    )

    items = []

    for index, post in enumerate(
        posts,
        start=1,
    ):

        label = (
            f"@{post.account}"
        )

        if post.timestamp:

            label += (
                f" — {post.timestamp}"
            )

        items.append(
            '<li>'
            '<a href="posts.xhtml#post-'
            f'{index}">'
            f'{escape_text(label)}'
            '</a>'
            '</li>'
        )

    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops">
<head>
<meta charset="utf-8"/>
<title>{escape_text(title)}</title>
<link rel="stylesheet" type="text/css"
      href="styles/style.css"/>
</head>
<body>
<main>
<h1>{escape_text(title)}</h1>
<ol class="toc">
{''.join(items)}
</ol>
</main>
</body>
</html>
"""


def nav_xhtml(
    date_value: str,
) -> str:

    title = (
        f"X Archive — {date_value}"
    )

    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:epub="http://www.idpf.org/2007/ops">
<head>
<meta charset="utf-8"/>
<title>{escape_text(title)}</title>
<link rel="stylesheet" type="text/css"
      href="styles/style.css"/>
</head>
<body>

<nav epub:type="toc"
     id="toc">

<h1>Contents</h1>

<ol>
<li>
<a href="cover.xhtml">
Cover
</a>
</li>

<li>
<a href="toc.xhtml">
Posts
</a>
</li>

</ol>

</nav>

</body>
</html>
"""


# ============================================================
# EPUB package
# ============================================================

def container_xml() -> bytes:

    return b"""<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0"
 xmlns="urn:oasis:names:tc:opendocument:xmlns:container">

<rootfiles>

<rootfile
 full-path="OEBPS/content.opf"
 media-type="application/oebps-package+xml"/>

</rootfiles>

</container>
"""


def content_opf(
    date_value: str,
    posts: list[Post],
    images: list[BookImage],
) -> str:

    book_id = (
        "urn:xarchive:"
        f"{date_value}"
    )

    title = (
        f"X Archive — {date_value}"
    )

    manifest = [

        '<item id="nav" '
        'href="nav.xhtml" '
        'media-type="application/xhtml+xml" '
        'properties="nav"/>',

        '<item id="cover" '
        'href="cover.xhtml" '
        'media-type="application/xhtml+xml"/>',

        '<item id="toc" '
        'href="toc.xhtml" '
        'media-type="application/xhtml+xml"/>',

        '<item id="posts" '
        'href="posts.xhtml" '
        'media-type="application/xhtml+xml"/>',

        '<item id="css" '
        'href="styles/style.css" '
        'media-type="text/css"/>',
    ]

    for index, image in enumerate(
        images,
        start=1,
    ):

        item_id = (
            f"image-{index}"
        )

        filename = Path(
            image.epub_path
        ).name

        manifest.append(
            f'<item id="{item_id}" '
            f'href="images/{escape_text(filename)}" '
            'media-type="image/jpeg"/>'
        )

    spine = [
        '<itemref idref="cover"/>',
        '<itemref idref="toc"/>',
        '<itemref idref="posts"/>',
    ]

    return f"""<?xml version="1.0" encoding="utf-8"?>

<package
 xmlns="http://www.idpf.org/2007/opf"
 version="3.0"
 unique-identifier="book-id">

<metadata
 xmlns:dc="http://purl.org/dc/elements/1.1/">

<dc:identifier id="book-id">
{escape_text(book_id)}
</dc:identifier>

<dc:title>
{escape_text(title)}
</dc:title>

<dc:language>zh</dc:language>

<dc:creator>
X Archive
</dc:creator>

<meta property="dcterms:modified">
{datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
</meta>

</metadata>

<manifest>
{''.join(manifest)}
</manifest>

<spine>
{''.join(spine)}
</spine>

</package>
"""


# ============================================================
# EPUB writing
# ============================================================

def write_epub(
    output: Path,
    date_value: str,
    posts: list[Post],
    image_map: dict[str, BookImage],
    temp_dir: Path,
) -> None:

    unique_images: list[BookImage] = []

    seen: set[str] = set()

    for image in image_map.values():

        if image.epub_path in seen:
            continue

        seen.add(
            image.epub_path
        )

        unique_images.append(
            image
        )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_output = (
        output.with_suffix(
            output.suffix + ".tmp"
        )
    )

    if temporary_output.exists():

        temporary_output.unlink()

    try:

        with zipfile.ZipFile(
            temporary_output,
            "w",
            compression=zipfile.ZIP_DEFLATED,
            compresslevel=9,
        ) as epub:

            # ------------------------------------------------
            # EPUB specification:
            # mimetype must be the first entry and STORED.
            # ------------------------------------------------

            info = zipfile.ZipInfo(
                "mimetype"
            )

            info.compress_type = (
                zipfile.ZIP_STORED
            )

            epub.writestr(
                info,
                b"application/epub+zip",
            )

            epub.writestr(
                "META-INF/container.xml",
                container_xml(),
            )

            epub.writestr(
                "OEBPS/styles/style.css",
                BOOK_CSS.encode(
                    "utf-8"
                ),
            )

            epub.writestr(
                "OEBPS/cover.xhtml",
                create_cover_xhtml(
                    date_value,
                    len(posts),
                ).encode(
                    "utf-8"
                ),
            )

            epub.writestr(
                "OEBPS/toc.xhtml",
                create_toc_xhtml(
                    date_value,
                    posts,
                ).encode(
                    "utf-8"
                ),
            )

            epub.writestr(
                "OEBPS/nav.xhtml",
                nav_xhtml(
                    date_value
                ).encode(
                    "utf-8"
                ),
            )

            epub.writestr(
                "OEBPS/posts.xhtml",
                create_posts_xhtml(
                    date_value,
                    posts,
                    image_map,
                ).encode(
                    "utf-8"
                ),
            )

            epub.writestr(
                "OEBPS/content.opf",
                content_opf(
                    date_value,
                    posts,
                    unique_images,
                ).encode(
                    "utf-8"
                ),
            )

            # ------------------------------------------------
            # Embed optimized images.
            # ------------------------------------------------

            for image in unique_images:

                prepared_file = (
                    temp_dir
                    / Path(
                        image.epub_path
                    ).name
                )

                if not prepared_file.exists():

                    raise RuntimeError(
                        "Prepared image is missing: "
                        f"{prepared_file}"
                    )

                epub.write(
                    prepared_file,
                    image.epub_path,
                )

        # ----------------------------------------------------
        # Atomic replacement.
        # ----------------------------------------------------

        temporary_output.replace(
            output
        )

    except Exception:

        if temporary_output.exists():

            temporary_output.unlink()

        raise


# ============================================================
# EPUB validation
# ============================================================

def validate_epub(
    output: Path,
) -> None:

    if not output.exists():

        raise RuntimeError(
            f"EPUB output does not exist: "
            f"{output}"
        )

    if output.stat().st_size == 0:

        raise RuntimeError(
            "EPUB output is empty."
        )

    with zipfile.ZipFile(
        output,
        "r",
    ) as epub:

        names = epub.namelist()

        if not names:

            raise RuntimeError(
                "EPUB archive is empty."
            )

        if names[0] != "mimetype":

            raise RuntimeError(
                "EPUB mimetype is not "
                "the first ZIP entry."
            )

        if (
            epub.getinfo(
                "mimetype"
            ).compress_type
            != zipfile.ZIP_STORED
        ):

            raise RuntimeError(
                "EPUB mimetype must not "
                "be compressed."
            )

        required = {
            "mimetype",
            "META-INF/container.xml",
            "OEBPS/content.opf",
            "OEBPS/nav.xhtml",
            "OEBPS/cover.xhtml",
            "OEBPS/toc.xhtml",
            "OEBPS/posts.xhtml",
            "OEBPS/styles/style.css",
        }

        missing = (
            required
            - set(names)
        )

        if missing:

            raise RuntimeError(
                "EPUB missing required files: "
                + ", ".join(
                    sorted(missing)
                )
            )

        bad = epub.testzip()

        if bad:

            raise RuntimeError(
                f"Corrupt EPUB member: {bad}"
            )

        # ----------------------------------------------------
        # Validate embedded images.
        # ----------------------------------------------------

        image_entries = [
            name
            for name in names
            if name.startswith(
                "OEBPS/images/"
            )
            and name.lower().endswith(
                ".jpg"
            )
        ]

        for name in image_entries:

            data = epub.read(
                name
            )

            if not data:

                raise RuntimeError(
                    f"Embedded image is empty: "
                    f"{name}"
                )


# ============================================================
# Main
# ============================================================

def main() -> int:

    args = parse_args()

    date_value = args.date

    validate_date(
        date_value
    )

    log(
        f"X Archive EPUB Builder "
        f"v{VERSION}"
    )

    log(
        f"Repository: {repo_root()}"
    )

    log(
        f"Archive date: {date_value}"
    )

    archive_dir = archive_directory(
        date_value
    )

    log(
        f"Archive directory: "
        f"{archive_dir}"
    )

    posts = load_posts(
        archive_dir
    )

    log(
        f"Markdown files: "
        f"{len(posts)}"
    )

    total_image_references = sum(
        len(post.image_urls)
        for post in posts
    )

    log(
        f"Image references: "
        f"{total_image_references}"
    )

    # --------------------------------------------------------
    # Safety:
    # A post that has image references must have those
    # images resolved before we create the EPUB.
    # --------------------------------------------------------

    with tempfile.TemporaryDirectory(
        prefix="xarchive-epub-"
    ) as temporary_directory:

        temp_dir = Path(
            temporary_directory
        )

        (
            image_map,
            processed,
            deduplicated,
            reference_count,
            failures,
        ) = build_image_assets(
            posts,
            temp_dir,
        )

        log(
            f"Images processed: "
            f"{processed}"
        )

        log(
            f"Images deduplicated: "
            f"{deduplicated}"
        )

        log(
            f"Image references resolved: "
            f"{len(image_map)}"
        )

        log(
            f"Image failures: "
            f"{failures}"
        )

        # ----------------------------------------------------
        # FAIL SAFE
        # ----------------------------------------------------

        if failures > 0:

            log(
                "ERROR: EPUB build aborted."
            )

            log(
                "ERROR: One or more referenced "
                "images could not be resolved "
                "or processed."
            )

            log(
                "ERROR: Existing EPUB was NOT "
                "modified."
            )

            return 2

        if (
            reference_count
            != len(image_map)
        ):

            log(
                "ERROR: Image reference count "
                "does not match resolved "
                "image count."
            )

            return 2

        # ----------------------------------------------------
        # Determine output.
        # ----------------------------------------------------

        if args.output:

            output = Path(
                args.output
            ).expanduser()

            if not output.is_absolute():

                output = (
                    repo_root()
                    / output
                )

        else:

            output = (
                output_directory()
                / (
                    f"{date_value}"
                    "-x-archive.epub"
                )
            )

        log(
            f"Output: {output}"
        )

        # ----------------------------------------------------
        # Build.
        # ----------------------------------------------------

        try:

            write_epub(
                output=output,
                date_value=date_value,
                posts=posts,
                image_map=image_map,
                temp_dir=temp_dir,
            )

        except Exception as exc:

            log(
                f"ERROR: EPUB creation failed: "
                f"{exc}"
            )

            return 2

        # ----------------------------------------------------
        # Validate.
        # ----------------------------------------------------

        try:

            validate_epub(
                output
            )

        except Exception as exc:

            log(
                f"ERROR: EPUB validation failed: "
                f"{exc}"
            )

            return 2

    size_mb = (
        output.stat().st_size
        / (1024 * 1024)
    )

    print()

    print("=" * 52)
    print("X Archive EPUB Result")
    print("=" * 52)

    print(
        f"Version:              {VERSION}"
    )

    print(
        f"Date:                 {date_value}"
    )

    print(
        f"Markdown files:       {len(posts)}"
    )

    print(
        f"Image references:     {reference_count}"
    )

    print(
        f"Images processed:     {processed}"
    )

    print(
        f"Images deduplicated:  {deduplicated}"
    )

    print(
        f"Image failures:       {failures}"
    )

    print(
        f"Image max width:      "
        f"{MAX_IMAGE_WIDTH}px"
    )

    print(
        f"JPEG quality:         "
        f"{JPEG_QUALITY}"
    )

    print(
        f"EPUB size:            "
        f"{size_mb:.2f} MB"
    )

    print(
        f"Output:               {output}"
    )

    print(
        "Validation:           PASSED"
    )

    print("=" * 52)

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
