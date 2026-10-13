#!/usr/bin/env python3
"""
Process raw Bluesky firehose data into simplified derived fields.

Input: data/incoming/firehose/unsorted/<dataset_tag>.json
Output: data/processing/<dataset_tag>/<dataset_tag>__stage0_0.json

Usage:
    python derive_fields.py <dataset_tag>

Example:
    python derive_fields.py random_100
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


def extract_media_urls(embed: Dict[str, Any]) -> List[str]:
    """Extract CDN URLs from embed objects."""
    urls = []

    if not embed:
        return urls

    embed_type = embed.get("$type", "")

    # Handle images
    if embed_type == "app.bsky.embed.images":
        for img in embed.get("images", []):
            if "image" in img and "ref" in img["image"]:
                ref = img["image"]["ref"].get("$link", "")
                if ref:
                    # Bluesky CDN URL format
                    urls.append(f"https://cdn.bsky.app/img/feed_fullsize/plain/{ref}@jpeg")

    # Handle video
    elif embed_type == "app.bsky.embed.video":
        if "video" in embed and "ref" in embed["video"]:
            ref = embed["video"]["ref"].get("$link", "")
            if ref:
                urls.append(f"https://video.bsky.app/watch/{ref}")

    # Handle external embeds with thumbnails
    elif embed_type == "app.bsky.embed.external":
        external = embed.get("external", {})
        if "thumb" in external and "ref" in external["thumb"]:
            ref = external["thumb"]["ref"].get("$link", "")
            if ref:
                urls.append(f"https://cdn.bsky.app/img/feed_thumbnail/plain/{ref}@jpeg")

    # Handle record with media (quote posts with images/video)
    elif embed_type == "app.bsky.embed.recordWithMedia":
        media = embed.get("media", {})
        urls.extend(extract_media_urls(media))

    return urls


def count_facet_features(facets: List[Dict[str, Any]], feature_type: str) -> int:
    """Count number of facets with a specific feature type."""
    if not facets:
        return 0

    count = 0
    for facet in facets:
        for feature in facet.get("features", []):
            if feature.get("$type", "") == feature_type:
                count += 1

    return count


def clean_text(text: str) -> str:
    """Clean and normalize post text."""
    if not text:
        return ""

    # Remove extra whitespace
    cleaned = re.sub(r'\s+', ' ', text)

    # Strip leading/trailing whitespace
    cleaned = cleaned.strip()

    return cleaned


def process_post(item: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single firehose item into derived fields."""
    # Skip non-post items
    if item.get("kind") != "commit":
        return None

    commit = item.get("commit", {})
    if commit.get("collection") != "app.bsky.feed.post":
        return None

    record = commit.get("record", {})
    if record.get("$type") != "app.bsky.feed.post":
        return None

    # Extract embed information
    embed = record.get("embed", {})
    embed_type = embed.get("$type", "")

    # Determine media flags
    has_images = embed_type in [
        "app.bsky.embed.images",
    ] or (embed_type == "app.bsky.embed.recordWithMedia" and
          embed.get("media", {}).get("$type") == "app.bsky.embed.images")

    has_video = embed_type == "app.bsky.embed.video" or (
        embed_type == "app.bsky.embed.recordWithMedia" and
        embed.get("media", {}).get("$type") == "app.bsky.embed.video"
    )

    # Determine post type
    is_reply = "reply" in record
    is_quote_post = embed_type in ["app.bsky.embed.record", "app.bsky.embed.recordWithMedia"]

    # Count facets
    facets = record.get("facets", [])
    mention_count = count_facet_features(facets, "app.bsky.richtext.facet#mention")
    link_count = count_facet_features(facets, "app.bsky.richtext.facet#link")

    # Extract media URLs
    media_urls = extract_media_urls(embed)

    # Clean text
    text = record.get("text", "")
    cleaned_text = clean_text(text)

    # Build derived record
    derived = {
        "did": item.get("did"),
        "timestamp": record.get("createdAt"),
        "uri": f"at://{item.get('did')}/app.bsky.feed.post/{commit.get('rkey')}",
        "has_images": has_images,
        "has_video": has_video,
        "is_reply": is_reply,
        "is_quote_post": is_quote_post,
        "mention_count": mention_count,
        "link_count": link_count,
        "media_urls": media_urls,
        "cleaned_text": cleaned_text,
        "original_text": text,
        "langs": record.get("langs", []),
    }

    return derived


def main():
    """Main processing function."""
    if len(sys.argv) != 2:
        print("Usage: python derive_fields.py <dataset_tag>")
        print("Example: python derive_fields.py random_100")
        sys.exit(1)

    dataset_tag = sys.argv[1]

    input_path = Path(f"data/incoming/firehose/unsorted/{dataset_tag}.json")
    output_dir = Path(f"data/processing/{dataset_tag}")
    output_path = output_dir / f"{dataset_tag}__stage0_0.json"

    print(f"Reading from: {input_path}")

    # Load raw data
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    print(f"Loaded {len(raw_data)} raw items")

    # Process each item
    processed_items = []
    for item in raw_data:
        derived = process_post(item)
        if derived:
            processed_items.append(derived)

    print(f"Processed {len(processed_items)} posts")

    # Save processed data
    output_dir.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_items, f, indent=2, ensure_ascii=False)

    print(f"Saved to: {output_path}")

    # Print summary statistics
    print("\n=== Summary Statistics ===")
    print(f"Total posts: {len(processed_items)}")
    print(f"Posts with images: {sum(1 for p in processed_items if p['has_images'])}")
    print(f"Posts with video: {sum(1 for p in processed_items if p['has_video'])}")
    print(f"Replies: {sum(1 for p in processed_items if p['is_reply'])}")
    print(f"Quote posts: {sum(1 for p in processed_items if p['is_quote_post'])}")
    print(f"Posts with mentions: {sum(1 for p in processed_items if p['mention_count'] > 0)}")
    print(f"Posts with links: {sum(1 for p in processed_items if p['link_count'] > 0)}")
    print(f"Posts with media URLs: {sum(1 for p in processed_items if p['media_urls'])}")


if __name__ == "__main__":
    main()
