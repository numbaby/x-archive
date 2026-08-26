#!/usr/bin/env python3

import argparse
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

POSTS_DIR = ROOT / "data" / "posts"
ARCHIVE_DIR = ROOT / "archive"


def load_posts(path):

    posts = []

    with path.open(
        "r",
        encoding="utf-8"
    ) as f:

        for line in f:

            line = line.strip()

            if not line:
                continue

            posts.append(json.loads(line))

    return posts


def escape_alt_text(text):

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text[:200]


def relative_image_path(
    markdown_file,
    image_path
):

    image = ROOT / image_path

    return os.path.relpath(
        image,
        markdown_file.parent
    ).replace("\\", "/")


def render_post(
    post,
    markdown_file
):

    published = datetime.fromisoformat(
        post["published_at"].replace("Z", "+00:00")
    ).astimezone(timezone.utc)

    username = post["account"]["username"]

    time_text = published.strftime(
        "%H:%M UTC"
    )

    content = post["content"].strip()

    lines = []

    lines.append(
        f"### 🕐 {time_text} · @{username}"
    )

    lines.append("")

    if content:

        for line in content.splitlines():

            line = line.rstrip()

            if line:
                lines.append(
                    f"> {line}"
                )
            else:
                lines.append(">")

    lines.append("")

    for media in post.get("media", []):

        local_path = media.get("local_path")

        if not local_path:
            continue

        image = relative_image_path(
            markdown_file,
            local_path
        )

        alt = escape_alt_text(
            post["content"]
        )

        lines.append(
            f"![{alt}]({image})"
        )

        lines.append("")

    lines.append(
        f"🔗 [View original post]({post['url']})"
    )

    lines.append("")

    lines.append("---")

    lines.append("")

    return "\n".join(lines)


def render_file(jsonl_file):

    posts = load_posts(jsonl_file)

    if not posts:
        return None

    posts.sort(
        key=lambda p: p["published_at"],
        reverse=True
    )

    first = datetime.fromisoformat(
        posts[0]["published_at"].replace("Z", "+00:00")
    ).astimezone(timezone.utc)

    year = first.strftime("%Y")
    month = first.strftime("%m")
    day = first.strftime("%d")

    output_dir = (
        ARCHIVE_DIR
        / year
        / month
        / day
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    accounts = sorted(
        {
            p["account"]["username"]
            for p in posts
        }
    )

    # Generate one file per account.
    outputs = []

    for username in accounts:

        account_posts = [
            p for p in posts
            if p["account"]["username"] == username
        ]

        markdown_file = (
            output_dir
            / f"{username}.md"
        )

        title_date = first.strftime(
            "%B %d, %Y"
        )

        lines = []

        lines.append(
            f"# 🐦 @{username}"
        )

        lines.append("")

        lines.append(
            f"## 📅 {title_date}"
        )

        lines.append("")

        lines.append(
            f"> {len(account_posts)} post(s) archived."
        )

        lines.append("")

        lines.append("---")

        lines.append("")

        for post in account_posts:

            lines.append(
                render_post(
                    post,
                    markdown_file
                )
            )

        markdown_file.write_text(
            "\n".join(lines),
            encoding="utf-8"
        )

        outputs.append(markdown_file)

    return outputs


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--file",
        help="Render one JSONL file"
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Render all JSONL files"
    )

    args = parser.parse_args()

    if args.file:

        result = render_file(
            Path(args.file)
        )

        if result:
            for path in result:
                print(
                    f"Rendered: {path.relative_to(ROOT)}"
                )

        return 0

    if args.all:

        files = sorted(
            POSTS_DIR.rglob("*.jsonl")
        )

        for path in files:
            render_file(path)

        print(
            f"Rendered {len(files)} JSONL file(s)"
        )

        return 0

    parser.error(
        "Specify --file or --all"
    )


if __name__ == "__main__":
    main()
