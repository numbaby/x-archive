#!/usr/bin/env python3
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent

# Since it's 2026-08-26 22:16 UTC, we need posts since 2026-08-26 00:00:00 UTC
# UPDATE THIS BEFORE EACH RUN
CUTOFF = datetime(2026, 8, 26, 0, 0, 0, tzinfo=timezone.utc)

# Profiles from the JSON
profiles = [
    "elonmusk",
    "Fiction_1m",
    "_Regret_x",
    "Turbo_clips",
    "Alphafiles1",
    "theendeavorpath",
    "alone_boy_010",
    "Wise1Philosophy",
    "Letstalk246",
    "LimitlessLif3",
    "voidfeels_1",
    "Unlockyourlife_",
]

def fetch_feed(username):
    """Fetch Atom feed from fxtwitter."""
    url = f"https://fxtwitter.com/{username}/feed.atom.xml"
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 X-Archive/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read()
    except Exception as e:
        print(f"ERROR fetching {username}: {e}", file=sys.stderr)
        return None

def parse_atom_feed(xml_data, username):
    """Parse Atom feed and extract posts since cutoff."""
    if not xml_data:
        return []
    
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError as e:
        print(f"ERROR parsing XML for {username}: {e}", file=sys.stderr)
        return []
    
    # Atom namespace
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    
    posts = []
    for entry in root.findall("atom:entry", ns):
        # Get published date
        published_elem = entry.find("atom:published", ns)
        updated_elem = entry.find("atom:updated", ns)
        
        pub_str = published_elem.text if published_elem is not None else None
        if not pub_str:
            pub_str = updated_elem.text if updated_elem is not None else None
        
        if not pub_str:
            continue
        
        # Parse date
        try:
            published = datetime.fromisoformat(pub_str.replace("Z", "+00:00"))
            if published.tzinfo is None:
                published = published.replace(tzinfo=timezone.utc)
            else:
                published = published.astimezone(timezone.utc)
        except ValueError:
            continue
        
        # Filter by cutoff
        if published < CUTOFF:
            continue
        
        # Get post ID from link
        link_elem = entry.find("atom:link[@rel='alternate']", ns)
        post_url = link_elem.get("href") if link_elem is not None else ""
        
        # Extract post ID from URL
        post_id_match = re.search(r"/status/(\d+)", post_url)
        post_id = post_id_match.group(1) if post_id_match else ""
        
        # Get content
        content_elem = entry.find("atom:content", ns)
        content_html = content_elem.text if content_elem is not None else ""
        
        # Extract text from HTML (simple approach)
        content_text = re.sub(r"<[^>]+>", "", content_html)
        content_text = re.sub(r"&nbsp;", " ", content_text)
        content_text = re.sub(r"&", "&", content_text)
        content_text = re.sub(r"<", "<", content_text)
        content_text = re.sub(r">", ">", content_text)
        content_text = re.sub(r"\s+", " ", content_text).strip()
        
        # Get media URLs
        media = []
        for link in entry.findall("atom:link[@rel='enclosure']", ns):
            media_url = link.get("href")
            media_type = link.get("type", "")
            if media_url:
                m_type = "image"
                if "video" in media_type:
                    m_type = "video"
                elif "gif" in media_type:
                    m_type = "gif"
                media.append({
                    "type": m_type,
                    "source_url": media_url
                })
        
        # Build post object
        post = {
            "id": post_id,
            "platform": "x",
            "account": {
                "username": username
            },
            "published_at": published.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "content": content_text,
            "url": post_url,
            "media": media,
            "metadata": {
                "collected_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "collector": "hermes"
            }
        }
        
        posts.append(post)
    
    return posts

def main():
    all_posts = []
    
    for username in profiles:
        print(f"Fetching {username}...", file=sys.stderr)
        xml_data = fetch_feed(username)
        posts = parse_atom_feed(xml_data, username)
        print(f"  Found {len(posts)} new posts", file=sys.stderr)
        all_posts.extend(posts)
    
    # Write to incoming directory
    incoming_dir = ROOT / "incoming"
    incoming_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    output_file = incoming_dir / f"posts_{timestamp}.json"
    
    with output_file.open("w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False, indent=2)
    
    print(f"\nWritten {len(all_posts)} posts to {output_file}", file=sys.stderr)
    return 0

if __name__ == "__main__":
    sys.exit(main())