# Random 100 Processing Summary

**Date:** 2026-10-13
**Input:** `data/incoming/firehose/unsorted/random_100.json`
**Output:** `data/processing/random_100/processed.json`
**Script:** `process_random_100.py`

## Overview

Successfully processed 100 raw Bluesky firehose messages into simplified derived fields for analysis. The processing follows the naming convention where the raw capture filename determines the processing directory name.

## Derived Fields Extracted

### Media Detection
- `has_images` - Boolean flag for image content
- `has_video` - Boolean flag for video content
- `media_urls` - Resolved CDN URLs for all media (images, videos, thumbnails)

### Post Type Classification
- `is_reply` - Identifies reply posts
- `is_quote_post` - Identifies quote posts (including recordWithMedia embeds)

### Facet Counts
- `mention_count` - Number of @mentions in the post
- `link_count` - Number of embedded links in the post

### Text Processing
- `cleaned_text` - Normalized text with whitespace condensed and trimmed
- `original_text` - Preserved original text for reference

### Additional Metadata
- `did` - User DID
- `timestamp` - Post creation timestamp
- `uri` - AT Protocol URI for the post
- `langs` - Language tags

## Results Summary

From 100 posts processed:

| Metric | Count | Percentage |
|--------|-------|------------|
| Total posts | 100 | 100% |
| Posts with images | 9 | 9% |
| Posts with video | 2 | 2% |
| Replies | 54 | 54% |
| Quote posts | 9 | 9% |
| Posts with mentions | 4 | 4% |
| Posts with links | 14 | 14% |
| Posts with media URLs | 24 | 24% |

## Implementation Details

### Media URL Resolution

The script resolves blob references to actual CDN URLs:

- **Images:** `https://cdn.bsky.app/img/feed_fullsize/plain/{ref}@jpeg`
- **Videos:** `https://video.bsky.app/watch/{ref}`
- **Thumbnails:** `https://cdn.bsky.app/img/feed_thumbnail/plain/{ref}@jpeg`

### Supported Embed Types

- `app.bsky.embed.images` - Image posts
- `app.bsky.embed.video` - Video posts
- `app.bsky.embed.external` - External links with thumbnails
- `app.bsky.embed.record` - Quote posts
- `app.bsky.embed.recordWithMedia` - Quote posts with media

### Facet Processing

Facets are parsed to count:
- `app.bsky.richtext.facet#mention` - User mentions
- `app.bsky.richtext.facet#link` - Embedded URLs

## File Organization

```
data/
├── incoming/firehose/unsorted/
│   └── random_100.json          # Raw capture
└── processing/random_100/
    └── processed.json            # Derived dataset
```

The naming convention ensures clear traceability between raw captures and their processed outputs.

## Next Steps

This derived dataset can now be used for:
- Content analysis and categorization
- Media usage patterns
- Engagement metrics (reply rates, quote rates)
- Link and mention network analysis
- Language distribution studies
