"""Demonstration script for fetching media from BlueSky posts.

This script:
1. Iterates through posts in random_100.json
2. Finds the first post with media (images or video)
3. Downloads the media using the BlueSky CDN
4. Saves it to explore/tmp/

This demonstrates how to resolve IPFS CIDs to actual media files.
"""

import json
from pathlib import Path
import requests
import random


def find_post_with_media(posts_file: Path) -> dict | None:
    """Find first post with media embed.

    Args:
        posts_file: Path to JSON file containing posts

    Returns:
        Post dict with media, or None if not found
    """
    with open(posts_file) as f:
        posts = json.load(f)
        random.shuffle(posts)


    for post in posts:
        record = post.get("commit", {}).get("record", {})
        embed = record.get("embed", {})
        embed_type = embed.get("$type", "")

        # Check for images or video
        if embed_type in ("app.bsky.embed.images", "app.bsky.embed.video"):
            return post

    return None


def download_media(post: dict, output_dir: Path) -> list[Path]:
    """Download media from a post.

    Args:
        post: Post dict containing media embed
        output_dir: Directory to save media files

    Returns:
        List of paths to downloaded files
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    did = post["did"]
    record = post["commit"]["record"]
    embed = record["embed"]
    embed_type = embed["$type"]

    downloaded = []

    if embed_type == "app.bsky.embed.images":
        # Download each image
        for i, img_data in enumerate(embed["images"]):
            cid = img_data["image"]["ref"]["$link"]
            mime_type = img_data["image"]["mimeType"]

            # Determine file extension
            ext = mime_type.split("/")[-1]

            # Construct CDN URL
            url = f"https://cdn.bsky.app/img/feed_thumbnail/plain/{did}/{cid}@{ext}"

            # Download
            response = requests.get(url)
            response.raise_for_status()

            # Save
            filename = f"image_{i}_{cid[:12]}.{ext}"
            filepath = output_dir / filename
            filepath.write_bytes(response.content)
            downloaded.append(filepath)

            print(f"Downloaded: {filename} ({len(response.content)} bytes)")

    elif embed_type == "app.bsky.embed.video":
        # Download video
        cid = embed["video"]["ref"]["$link"]
        mime_type = embed["video"]["mimeType"]

        # Determine file extension
        ext = mime_type.split("/")[-1]

        # Construct CDN URL (note: different pattern for video)
        url = f"https://video.bsky.app/watch/{did}/{cid}/thumbnail.jpg"

        # Try thumbnail first, fall back to alternate formats
        try:
            response = requests.get(url)
            response.raise_for_status()
        except:
            # Try alternate CDN format
            url = f"https://cdn.bsky.app/img/feed_thumbnail/plain/{did}/{cid}@{ext}"
            response = requests.get(url)
            response.raise_for_status()

        # Save
        filename = f"video_{cid[:12]}.{ext}"
        filepath = output_dir / filename
        filepath.write_bytes(response.content)
        downloaded.append(filepath)

        print(f"Downloaded: {filename} ({len(response.content)} bytes)")

    return downloaded


def main():
    """Run the demonstration."""
    # Paths
    posts_file = Path("data/incoming/firehose/unsorted/random_100.json")
    output_dir = Path("explore/tmp")

    print(f"Searching for posts with media in {posts_file}...")

    # Find post with media
    post = find_post_with_media(posts_file)

    if not post:
        print("No posts with media found!")
        return

    # Display post info
    record = post["commit"]["record"]
    embed = record["embed"]
    embed_type = embed["$type"]

    print(f"\nFound post with {embed_type}:")
    print(f"  Author DID: {post['did']}")
    print(f"  Text: {record.get('text', '(no text)')[:80]}...")
    print(f"  Created: {record['createdAt']}")

    if embed_type == "app.bsky.embed.images":
        print(f"  Images: {len(embed['images'])}")
    elif embed_type == "app.bsky.embed.video":
        print(f"  Video: {embed['video']['mimeType']}")

    print(f"\nDownloading media to {output_dir}...")

    # Download media
    downloaded = download_media(post, output_dir)

    print(f"\nSuccess! Downloaded {len(downloaded)} file(s):")
    for filepath in downloaded:
        print(f"  {filepath}")


if __name__ == "__main__":
    main()
