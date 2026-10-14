# BlueSky Data Access Methods

Analysis of alternative ways to access BlueSky posts beyond basic firehose sampling.

## Question 1: Getting Posts from a Specific Feed (Authenticated User)

The current codebase only uses the Jetstream firehose (anonymous, unauthenticated). To get posts from a specific feed for a signed-in user, you need to:

1. **Use the AT Protocol API directly** (not Jetstream firehose)
2. **Authenticate with your credentials**
3. **Call the feed generation endpoint**

### Implementation Approach

```python
from atproto import Client

# Authenticate
client = Client()
client.login('your-handle.bsky.social', 'your-app-password')

# Get posts from a specific feed
# Feed URIs look like: at://did:plc:xxx/app.bsky.feed.generator/yyy
feed_uri = "at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot"

# Or use well-known feeds
response = client.app.bsky.feed.get_feed({
    'feed': feed_uri,
    'limit': 50  # max 100
})

for feed_item in response.feed:
    post = feed_item.post
    # Access post data
```

### Common Feed URIs

- **What's Hot**: `at://did:plc:z72i7hdynmk6r22z27h6tvur/app.bsky.feed.generator/whats-hot`
- **Following feed**: Use `client.app.bsky.feed.get_timeline()` instead
- **Custom feeds**: Find them via `client.app.bsky.feed.get_actor_feeds(actor=did)`

## Question 2: Controls Available for Firehose Sampling

The current implementation (`firehose.py:11-50`) uses Jetstream with basic filtering (post creation events only).

### Available Jetstream Parameters

Jetstream accepts URL query parameters:

```python
# Add to JETSTREAM_URL
"wss://jetstream1.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post&wantedDids=did:plc:xxx,did:plc:yyy"
```

**Built-in controls:**
- `wantedCollections`: Filter by record type (NSID) - see detailed list below
- `wantedDids`: Filter by specific user DIDs (comma-separated) - see detailed list below
- `cursor`: Start from a specific point in time (microseconds since epoch)

#### `wantedCollections` - Detailed Options

Filters by **record type** (NSID). You can specify exact collections or use wildcards.

**Exact Collection NSIDs:**

**app.bsky.actor:**
- `app.bsky.actor.profile` - User profile records

**app.bsky.feed:**
- `app.bsky.feed.post` - Posts (most common for content collection)
- `app.bsky.feed.like` - Like declarations
- `app.bsky.feed.repost` - Reposts
- `app.bsky.feed.generator` - Feed generator declarations
- `app.bsky.feed.threadgate` - Thread reply controls
- `app.bsky.feed.postgate` - Post interaction rules

**app.bsky.graph:**
- `app.bsky.graph.follow` - Follow relationships
- `app.bsky.graph.block` - Block relationships
- `app.bsky.graph.list` - User lists
- `app.bsky.graph.listitem` - List membership records
- `app.bsky.graph.listblock` - List blocks
- `app.bsky.graph.starterpack` - Starter packs

**app.bsky.labeler:**
- `app.bsky.labeler.service` - Labeling service records

**Other available namespaces:**
- `app.bsky.bookmark.*` - Bookmarks
- `app.bsky.video.*` - Videos
- `app.bsky.draft.*` - Draft content
- `chat.bsky.*` - Chat messages

**Wildcard Prefixes:**

You can use `*` to match entire namespaces:
- `app.bsky.feed.*` - All feed-related records (posts, likes, reposts, etc.)
- `app.bsky.graph.*` - All graph records (follows, blocks, lists, etc.)
- `app.bsky.*` - Everything in app.bsky namespace

**Limits and Rules:**
- Max 100 collections/prefixes per subscription
- Prefix before `.*` must be a valid NSID
- You always receive Account and Identity events regardless of filters

**Example URLs:**
```python
# Only posts and likes
"wss://jetstream1.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post&wantedCollections=app.bsky.feed.like"

# Monitor social graph changes
"wss://jetstream1.us-east.bsky.network/subscribe?wantedCollections=app.bsky.graph.*"

# All feed activity
"wss://jetstream1.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.*"
```

#### `wantedDids` - Detailed Options

Filters by **user DID** (Decentralized Identifier).

**DID Format:**

DIDs look like: `did:plc:q6gjnaw2blty4crticxkmujt`

**How to obtain DIDs:**

1. **Resolve from handle:** Use AT Protocol API to convert `@username.bsky.social` to DID
   ```python
   from atproto import Client
   client = Client()
   profile = client.app.bsky.actor.get_profile({'actor': 'username.bsky.social'})
   did = profile.did
   ```

2. **Extract from firehose data:** DIDs appear in messages under `data['did']`

3. **From profile URLs:** Look up user profiles via API

**Limits:**
- Max 10,000 DIDs per subscription
- Comma-separated list in URL params

**Example URLs:**
```python
# Track specific users
"wss://jetstream1.us-east.bsky.network/subscribe?wantedDids=did:plc:abc123,did:plc:def456"

# Specific user's posts only
"wss://jetstream1.us-east.bsky.network/subscribe?wantedCollections=app.bsky.feed.post&wantedDids=did:plc:xyz789"

# Multiple users, only social graph activity
"wss://jetstream1.us-east.bsky.network/subscribe?wantedCollections=app.bsky.graph.*&wantedDids=did:plc:user1,did:plc:user2"
```

**Dynamic Updates:**

Sending empty `wantedDids` or `wantedCollections` resets the filter to receive all records again.

### What's NOT Available in Jetstream

- ❌ Keyword searches
- ❌ Embedding steering
- ❌ Content-based filtering
- ❌ Language filtering

### Post-Processing Filter Options

After receiving posts from the firehose, you can add custom filtering:

#### 1. Keyword Filtering

```python
if any(keyword in record.get('text', '').lower() for keyword in ['ai', 'machine learning']):
    yield data
```

#### 2. Username Filtering (handle or DID)

```python
if data['did'] in wanted_dids or data.get('commit', {}).get('record', {}).get('createdBy') == handle:
    yield data
```

#### 3. Language Detection

```python
from langdetect import detect
if detect(record.get('text', '')) == 'en':
    yield data
```

#### 4. Embedding-Based Filtering (expensive)

- Generate embeddings for post text
- Filter by cosine similarity to target embeddings
- This would be expensive to do in real-time
- Better as a batch post-processing step

## Recommendations

For optimal data collection strategy:

1. **For feed-specific posts**: Use authenticated API calls with `client.app.bsky.feed.get_feed()`
2. **For firehose sampling**: Add post-processing filters in `connect_firehose()` for keywords, users, etc.
3. **For embedding-based steering**: Collect posts first, then filter with embeddings as a batch process

### Hybrid Approach

Combine methods based on use case:
- Use API feeds for curated, algorithm-ranked content
- Use firehose with filters for real-time, comprehensive sampling
- Apply ML-based filtering (embeddings) as post-processing step
