#!/usr/bin/env python3

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import urllib.request

from jsonschema import Draft202012Validator
from jsonschema import FormatChecker


ROOT = Path(__file__).resolve().parent.parent

SCHEMA_FILE = ROOT / "schema" / "post.schema.json"
INDEX_FILE = ROOT / "data" / "index.json"

POSTS_DIR = ROOT / "data" / "posts"
ASSETS_DIR = ROOT / "assets" / "images"


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_index():
    if not INDEX_FILE.exists():
        return {}

    return load_json(INDEX_FILE)


def save_json_atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)

    fd, tmp_name = tempfile.mkstemp(
        prefix=path.name + ".",
        suffix=".tmp",
        dir=str(path.parent)
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2,
                sort_keys=True
            )
            f.write("\n")

        os.replace(tmp_name, path)

    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def validate_post(post, validator):
    errors = sorted(
        validator.iter_errors(post),
        key=lambda e: list(e.path)
    )

    if errors:
        print("ERROR: JSON validation failed")

        for error in errors:
            location = ".".join(str(x) for x in error.path)

            if not location:
                location = "<root>"

            print(f"  {location}: {error.message}")

        return False

    return True


def safe_filename(value):
    value = re.sub(r"[^A-Za-z0-9_.-]", "_", value)
    return value[:200]


def download_media(post):
    downloaded = 0
    failed = 0

    media_list = post.get("media", [])

    if not media_list:
        return downloaded, failed

    published = datetime.fromisoformat(
        post["published_at"].replace("Z", "+00:00")
    ).astimezone(timezone.utc)

    date_dir = (
        ASSETS_DIR
        / published.strftime("%Y")
        / published.strftime("%m")
        / published.strftime("%d")
    )

    date_dir.mkdir(parents=True, exist_ok=True)

    for index, media in enumerate(media_list, start=1):

        if media["type"] != "image":
            continue

        source_url = media["source_url"]

        parsed = urlparse(source_url)

        extension = Path(parsed.path).suffix.lower()

        if extension not in {
            ".jpg",
            ".jpeg",
            ".png",
            ".webp",
            ".gif"
        }:
            extension = ".jpg"

        filename = (
            f"{post['id']}-{index}{extension}"
        )

        target = date_dir / safe_filename(filename)

        relative_path = target.relative_to(ROOT).as_posix()

        media["local_path"] = relative_path

        if target.exists() and target.stat().st_size > 0:
            continue

        try:
            request = urllib.request.Request(
                source_url,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 "
                        "X-Archive/1.0"
                    )
                }
            )

            with urllib.request.urlopen(
                request,
                timeout=30
            ) as response:

                content = response.read()

            if not content:
                raise RuntimeError("empty response")

            target.write_bytes(content)

            downloaded += 1

        except Exception as exc:

            failed += 1

            print(
                f"WARNING: media download failed: "
                f"{source_url}: {exc}",
                file=sys.stderr
            )

            media.pop("local_path", None)

    return downloaded, failed


def append_jsonl(post):
    published = datetime.fromisoformat(
        post["published_at"].replace("Z", "+00:00")
    ).astimezone(timezone.utc)

    target = (
        POSTS_DIR
        / published.strftime("%Y")
        / published.strftime("%m")
        / f"{published.strftime('%Y-%m-%d')}.jsonl"
    )

    target.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with target.open(
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            json.dumps(
                post,
                ensure_ascii=False,
                separators=(",", ":")
            )
        )

        f.write("\n")

    return target


def post_fingerprint(post):
    raw = (
        post["account"]["username"]
        + "\n"
        + post["published_at"]
        + "\n"
        + post["content"]
    )

    return hashlib.sha256(
        raw.encode("utf-8")
    ).hexdigest()


def process_post(post, validator, index):

    if not validate_post(post, validator):
        raise ValueError(
            f"Invalid post: {post.get('id')}"
        )

    post_id = post["id"]

    if post_id in index:
        return {
            "status": "duplicate",
            "id": post_id,
            "downloaded": 0,
            "failed": 0
        }

    downloaded, failed = download_media(post)

    target = append_jsonl(post)

    published = datetime.fromisoformat(
        post["published_at"].replace("Z", "+00:00")
    ).astimezone(timezone.utc)

    index[post_id] = {
        "account": post["account"]["username"],
        "date": published.strftime("%Y-%m-%d"),
        "file": target.relative_to(ROOT).as_posix(),
        "fingerprint": post_fingerprint(post)
    }

    return {
        "status": "new",
        "id": post_id,
        "downloaded": downloaded,
        "failed": failed
    }


def main():

    parser = argparse.ArgumentParser(
        description="Archive X posts"
    )

    parser.add_argument(
        "input",
        help="JSON file containing one post or an array of posts"
    )

    args = parser.parse_args()

    input_file = Path(args.input)

    if not input_file.exists():
        print(
            f"ERROR: input not found: {input_file}",
            file=sys.stderr
        )
        return 2

    schema = load_json(SCHEMA_FILE)

    validator = Draft202012Validator(
        schema,
        format_checker=FormatChecker()
    )

    payload = load_json(input_file)

    if isinstance(payload, dict):
        posts = [payload]

    elif isinstance(payload, list):
        posts = payload

    else:
        print(
            "ERROR: input must be JSON object or array",
            file=sys.stderr
        )
        return 2

    index = load_index()

    new_count = 0
    duplicate_count = 0
    downloaded_count = 0
    failed_count = 0

    for post in posts:

        result = process_post(
            post,
            validator,
            index
        )

        if result["status"] == "duplicate":
            duplicate_count += 1

        else:
            new_count += 1

        downloaded_count += result["downloaded"]
        failed_count += result["failed"]

    save_json_atomic(
        INDEX_FILE,
        index
    )

    print()
    print("Archive result")
    print("======================")
    print(f"Discovered:        {len(posts)}")
    print(f"New:               {new_count}")
    print(f"Duplicates:        {duplicate_count}")
    print(f"Images downloaded: {downloaded_count}")
    print(f"Image failures:    {failed_count}")
    print(f"Index entries:     {len(index)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
