# Changes v0.0

## Completed Implementation

**Setup & Structure**
- Added `websockets` dependency to pyproject.toml
- Created `data/incoming/firehose/latest/` directory structure

**Firehose Client (firehose.py:1-95)**
- WebSocket connection to BlueSky Jetstream endpoint
- Message parsing and JSON handling
- Post filtering (only `app.bsky.feed.post` creation events)
- Configurable sampling with random selection
- Max posts limit

**Data Storage**
- JSON file output to `data/incoming/firehose/latest/`
- Timestamped filenames
- Pretty-printed JSON (indent=2)

**Main CLI (main.py:1-42)**
- `--sample-rate`: Control sampling fraction (0.0-1.0)
- `--max-posts`: Set collection limit
- `--output-dir`: Configure output location
- Clean argparse interface

**Testing**
- Successfully captured 3 posts with default settings
- Verified 10% sampling rate with 5 posts
- Both test files saved correctly

## Technical Details

**BlueSky Jetstream Endpoint**
- URL: `wss://jetstream1.us-east.bsky.network/subscribe`
- Public access (no authentication required)
- JSON-based firehose (easier than binary CBOR/CAR format)

**Post Filtering Logic**
```python
if data.get("kind") == "commit" and data.get("commit", {}).get("operation") == "create":
    record = data.get("commit", {}).get("record", {})
    if record.get("$type") == "app.bsky.feed.post":
        # This is a post creation event
```

**Design Principles Applied**
- Concise, readable code
- Brevity paramount
- Opinionated approach (Jetstream over raw firehose)
- Simple configuration (3 CLI args)
- No sprawling features

## Files Modified/Created

**Modified:**
- `pyproject.toml` - Added websockets dependency

**Created:**
- `firehose.py` - Core firehose client module
- `main.py` - CLI entry point (replaced placeholder)
- `data/incoming/firehose/latest/` - Output directory
- `planning/changes_v0.0.md` - This file

## Next Steps (Future Work)

From `planning/preliminary-plan-v1.0.md`, these remain as future enhancements:
- Database integration layer
- Ongoing monitoring mode
- Scale to 1M+ messages
- File rotation at 10MB limit (currently on hold)
- Advanced filtering/analysis
- Output format optimization
