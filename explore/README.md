# Explore

Experimental scripts for learning and testing BlueSky firehose functionality.

## Scripts

### `fetch_media_demo.py`

Demonstrates how to download media (images/videos) from BlueSky posts using IPFS CIDs.

**What it does:**
1. Reads posts from `data/incoming/firehose/unsorted/random_100.json`
2. Finds the first post with media (images or video)
3. Downloads media using BlueSky CDN
4. Saves to `explore/tmp/`

**Usage:**
```bash
uv run python explore/fetch_media_demo.py
```

**Key insights:**
- Media is referenced by IPFS CID in firehose, not embedded
- CDN URL pattern: `https://cdn.bsky.app/img/feed_thumbnail/plain/{did}/{cid}@{ext}`
- Images are typically ~100-500KB (thumbnails)
- Video URLs may require different CDN endpoints

## Directory Structure

```
explore/
├── README.md                  # This file
├── fetch_media_demo.py        # Media download demonstration
└── tmp/                       # Downloaded media (gitignored)
```
