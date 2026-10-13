# BlueSky Firehose JSON Format Analysis

**Date:** 2026-10-13
**Source:** Analysis of `data/incoming/firehose/unsorted/random_*.json` samples

## Overview

We're capturing complete raw messages from the BlueSky Jetstream firehose. This document analyzes what fields are available, what we're capturing, and how to handle media.

## Current Capture Strategy

**Status:** ✓ Capturing complete raw messages (correct approach)

Our `firehose.py` stores the entire message as-is, which gives us maximum flexibility for downstream processing.

## Message Structure

### Top-Level Fields

```json
{
  "did": "did:plc:...",           // User identifier
  "time_us": 1791911591007336,     // Timestamp (microseconds)
  "cursor": 25989416606,           // Firehose position marker
  "kind": "commit",                // Event type (we filter for this)
  "commit": { ... }                // The actual content
}
```

### Commit Structure

```json
{
  "rev": "3mxrjqx7dvm2h",          // AT Protocol revision
  "operation": "create",            // Operation type (we filter for this)
  "collection": "app.bsky.feed.post",
  "rkey": "3mxrjqwqhbc2d",
  "cid": "bafyreih...",            // Content identifier
  "record": { ... }                // The actual post data
}
```

### Post Record Fields

#### Always Present
- `$type`: "app.bsky.feed.post"
- `text`: Post text content
- `createdAt`: ISO 8601 timestamp
- `langs`: Array of language codes (e.g., `["en"]`)

#### Optional Fields

**1. Reply Threading**
```json
"reply": {
  "parent": {
    "cid": "bafyreiczenu...",
    "uri": "at://did:plc:.../app.bsky.feed.post/..."
  },
  "root": {
    "cid": "bafyreiczenu...",
    "uri": "at://did:plc:.../app.bsky.feed.post/..."
  }
}
```
- Indicates post is part of a conversation thread
- `parent`: Direct reply target
- `root`: Top-level thread starter

**2. Embeds** (Media & Links)

Four types observed in samples:

| Type | Count | Description |
|------|-------|-------------|
| `app.bsky.embed.external` | 17 | Link previews |
| `app.bsky.embed.record` | 9 | Quote posts |
| `app.bsky.embed.images` | 9 | Photos |
| `app.bsky.embed.video` | 2 | Videos/GIFs |

**3. Facets** (Rich Text)
```json
"facets": [
  {
    "$type": "app.bsky.richtext.facet",
    "features": [
      {
        "$type": "app.bsky.richtext.facet#mention",
        "did": "did:plc:..."
      }
    ],
    "index": {
      "byteStart": 0,
      "byteEnd": 25
    }
  }
]
```
- Mentions (`@username`)
- Links (URLs with positions)
- Hashtags (likely, not yet observed in samples)

**4. Bridgy Fields** (Mastodon Bridge)
- `bridgyOriginalText`: Original HTML from Mastodon
- `bridgyOriginalUrl`: Source URL on Mastodon

## Media Handling

### Image Embed Structure

```json
{
  "$type": "app.bsky.embed.images",
  "images": [
    {
      "alt": "Alt text for accessibility",
      "image": {
        "$type": "blob",
        "mimeType": "image/jpeg",
        "ref": {
          "$link": "bafkreicydlpm6voc3dfkergybmm5tflcnq3ijbfc2d5dh75l7l7wau43le"
        },
        "size": 138818
      }
    }
  ]
}
```

### Video Embed Structure

```json
{
  "$type": "app.bsky.embed.video",
  "aspectRatio": {
    "height": 281,
    "width": 500
  },
  "presentation": "gif",
  "video": {
    "$type": "blob",
    "mimeType": "video/mp4",
    "ref": {
      "$link": "bafkreie4uot7v5xmld6tmbchmt5bwdlvvpg2ydcym5j5sq43tvmkafdv2y"
    },
    "size": 44976
  }
}
```

### Key Media Insights

1. **Media is referenced, not embedded**
   - We get IPFS CIDs (`ref.$link`), not actual bytes
   - Firehose doesn't include image/video data

2. **To download media:**
   ```
   https://cdn.bsky.app/img/feed_thumbnail/plain/{did}/{cid}@jpeg
   ```
   - Replace `{did}` with post author's DID
   - Replace `{cid}` with the `$link` value
   - Thumbnails are ~100-500KB per image

3. **Media metadata available:**
   - Size in bytes
   - MIME type
   - Alt text (for images)
   - Aspect ratio (for videos)
   - Presentation hint (e.g., "gif")

## Recommendations

### Current Approach: ✓ Correct

**Keep storing complete raw messages**
- All fields are useful for different analyses
- Storage is cheap; completeness is valuable
- Efficient JSON format
- Enables flexible downstream processing

### Media Handling Strategy

**Option 1: References Only** (current)
- ✓ Minimal storage, fast ingestion
- ✓ Can decide later what to download
- ✗ Links may change/expire

**Option 2: Download Thumbnails**
- ✓ Always available for analysis
- ✗ ~100-500KB per image
- ✗ Slower ingestion, more bandwidth

**Option 3: Selective Download** (recommended)
- Store references for everything (current approach)
- Download media as separate processing step
- Apply filters: download only posts matching criteria
- Best of both: fast ingestion, selective preservation

### Suggested Architecture

```
Raw Capture (firehose.py)
    ↓
    └─ Store complete JSON (current)

Processing Pipeline (future)
    ↓
    ├─ Extract derived fields (has_images, is_reply, etc.)
    ├─ Clean/normalize text
    ├─ Resolve media URLs
    └─ Selective media download
```

## Fields We're NOT Missing

Analysis confirms we're capturing all available fields from the firehose. Any additional fields should be **derived** during processing, not added to raw capture:

- `has_images`, `has_video` (boolean flags)
- `is_reply`, `is_quote_post` (post type)
- `mention_count`, `link_count` (facet counts)
- `media_urls` (resolved CDN URLs)
- `cleaned_text` (processed version)

Keep raw capture clean and complete; add derived fields in processing layer.

## Summary

**Current state:** Excellent
**Changes needed:** None for raw capture
**Next steps:** Consider media download pipeline as separate concern
