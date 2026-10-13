"""BlueSky firehose sampler CLI."""

import asyncio
import argparse
from pathlib import Path
from firehose import collect_posts


def main():
    parser = argparse.ArgumentParser(
        description="Sample posts from BlueSky firehose"
    )
    parser.add_argument(
        "--sample-rate",
        type=float,
        default=1.0,
        help="Fraction of posts to sample (0.0 to 1.0, default: 1.0)",
    )
    parser.add_argument(
        "--max-posts",
        type=int,
        default=3,
        help="Maximum number of posts to collect (default: 3)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/incoming/firehose/unsorted"),
        help="Output directory (default: data/incoming/firehose/unsorted)",
    )

    args = parser.parse_args()

    asyncio.run(
        collect_posts(
            sample_rate=args.sample_rate,
            max_posts=args.max_posts,
            output_dir=args.output_dir,
        )
    )


if __name__ == "__main__":
    main()
