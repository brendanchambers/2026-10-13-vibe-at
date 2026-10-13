"""BlueSky firehose client using Jetstream WebSocket."""

import asyncio
import json
import websockets
from datetime import datetime
from pathlib import Path
from typing import AsyncIterator


JETSTREAM_URL = "wss://jetstream1.us-east.bsky.network/subscribe"


async def connect_firehose(
    sample_rate: float = 1.0,
    max_posts: int | None = None,
) -> AsyncIterator[dict]:
    """Connect to BlueSky Jetstream firehose and yield posts.

    Args:
        sample_rate: Fraction of posts to yield (0.0 to 1.0)
        max_posts: Maximum number of posts to yield (None for unlimited)

    Yields:
        Post messages from the firehose
    """
    import random

    post_count = 0

    async with websockets.connect(JETSTREAM_URL) as websocket:
        async for message in websocket:
            try:
                data = json.loads(message)

                # Filter for post creation events only
                if data.get("kind") == "commit" and data.get("commit", {}).get("operation") == "create":
                    record = data.get("commit", {}).get("record", {})
                    if record.get("$type") == "app.bsky.feed.post":
                        # Apply sampling
                        if random.random() < sample_rate:
                            post_count += 1
                            yield data

                            if max_posts and post_count >= max_posts:
                                return

            except json.JSONDecodeError:
                continue


def save_posts(posts: list[dict], output_dir: Path, dataset_tag: str | None = None) -> Path:
    """Save posts to JSON file.

    Args:
        posts: List of post messages
        output_dir: Directory to save the file
        dataset_tag: Optional tag to name the dataset (e.g., 'random_100')

    Returns:
        Path to the saved file
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    if dataset_tag:
        filepath = output_dir / f"{dataset_tag}.json"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = output_dir / f"posts_{timestamp}.json"

    with open(filepath, "w") as f:
        json.dump(posts, f, indent=2)

    return filepath


async def collect_posts(
    sample_rate: float = 1.0,
    max_posts: int = 3,
    output_dir: Path = Path("data/incoming/firehose/latest"),
    dataset_tag: str | None = None,
) -> Path:
    """Collect posts from firehose and save to file.

    Args:
        sample_rate: Fraction of posts to collect (0.0 to 1.0)
        max_posts: Number of posts to collect
        output_dir: Directory to save the file
        dataset_tag: Optional tag to name the dataset (e.g., 'random_100')

    Returns:
        Path to the saved file
    """
    posts = []

    print(f"Connecting to firehose (sample_rate={sample_rate}, max_posts={max_posts})...")

    async for post in connect_firehose(sample_rate=sample_rate, max_posts=max_posts):
        posts.append(post)
        print(f"Collected post {len(posts)}/{max_posts}")

    print(f"\nCollected {len(posts)} posts. Saving...")
    filepath = save_posts(posts, output_dir, dataset_tag=dataset_tag)
    print(f"Saved to: {filepath}")

    return filepath
