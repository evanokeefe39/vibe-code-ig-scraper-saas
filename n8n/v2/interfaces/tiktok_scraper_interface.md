# Actor Metadata
title: TikTok Data Extractor
description: Extracts TikTok video, user, and profile data from hashtags, profiles, search queries, or direct post URLs. Supports filtering, sorting, and selective media download.
version: 0.0
build_id: pJKuzTFcsuV7fnRMn

## Parameters

### hashtags
type: array[string]
description: List of TikTok hashtags (without the `#`) to scrape. The scraper collects videos containing any of these hashtags.
behavior: Each hashtag generates a separate query. The scraper extracts metadata such as video URL, user info, likes, and engagement counts.
example: ["ai", "fyp"]

### resultsPerPage
type: integer
minimum: 1
maximum: 1000000
default: 1
description: Number of videos to scrape per hashtag, profile, or search query.
behavior: Determines how many videos are collected from each source. Larger numbers increase runtime and cost.
example: 100

### profiles
type: array[string]
description: List of TikTok usernames to scrape (without @). Used for direct profile scraping.
behavior: Scrapes videos, reposts, and metadata from these user profiles. Ignores `searchQueries` if both provided.
example: ["sabrina_ramonov", "angus.sewell"]

### profileScrapeSections
type: array[string]
enum: ["videos", "reposts"]
default: ["videos"]
description: Defines which sections of a profile to scrape.
behavior: 
- `videos`: Scrapes the user's uploaded videos.
- `reposts`: Scrapes reposted videos by the user.
example: ["videos", "reposts"]

### profileSorting
type: string
enum: ["latest", "popular", "oldest"]
default: "latest"
description: Defines the order in which profile videos are scraped.
behavior: 
- `latest`: Scrapes newest videos first (compatible with date filters).
- `oldest`: Scrapes oldest videos first.
- `popular`: Scrapes most popular videos first.
example: "latest"

### oldestPostDateUnified
type: string
pattern: "^(\\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])(T[0-2]\\d:[0-5]\\d(:[0-5]\\d)?(\\.\\d+)?Z?)?$|^(\\d+)\\s*(minute|hour|day|week|month|year)s?$"
description: Lower date boundary for videos to scrape. Accepts ISO or relative durations (e.g., "3 days").
behavior: Filters videos to include only those posted after the specified date or within the relative timeframe.
example: "2 days"

### newestPostDate
type: string
description: Upper date boundary for videos to scrape. Accepts absolute ISO date format.
behavior: Filters videos to include only those published before or on this date.
example: "2025-11-04"

### excludePinnedPosts
type: boolean
default: false
description: Whether to exclude pinned posts from scraped profiles.
behavior: Pinned posts are usually the top few videos on a profile. Enabling this prevents duplicates or bias toward highlighted content.
example: true

### searchQueries
type: array[string]
description: Keywords or phrases to search TikTok for. Works with `searchSection` to determine scope.
behavior: Each query returns top videos or profiles, depending on `searchSection`. The scraper processes results up to `resultsPerPage`.
example: ["agentic rag", "n8n workflows", "ai tools"]

### searchSection
type: string
enum: ["", "/video", "/user"]
default: ""
description: Defines which TikTok search tab to use for results.
behavior:
- "": Searches top results (mixed types).
- "/video": Searches only videos.
- "/user": Searches only profiles.
example: "/video"

### maxProfilesPerQuery
type: integer
minimum: 1
default: 10
description: Maximum number of profiles to scrape per search query (used when `searchSection` is "/user").
behavior: Applies only when performing user-based searches. Ignores `resultsPerPage` for profile searches.
example: 1

### postURLs
type: array[string]
description: Direct TikTok video URLs to scrape.
behavior: When provided, the scraper focuses exclusively on these specific videos, ignoring hashtags or queries.
example: ["https://www.tiktok.com/@sabrina_ramonov/video/7332475328413855745"]

### shouldDownloadVideos
type: boolean
default: false
description: Whether to download the TikTok videos.
behavior: Downloads the full MP4 files into Apify storage. Increases runtime and storage cost significantly.
example: false

### shouldDownloadCovers
type: boolean
default: false
description: Whether to download video thumbnail images (covers).
behavior: Fetches the cover images for each scraped video and stores them in the dataset or key-value store.
example: false

### shouldDownloadSubtitles
type: boolean
default: false
description: Whether to download subtitles (if available) for videos.
behavior: Fetches subtitle text files and links them to each scraped video object.
example: false

### shouldDownloadSlideshowImages
type: boolean
default: false
description: Whether to download slideshow images from carousel-style posts.
behavior: Increases execution time and output size when enabled.
example: false

### videoKvStoreIdOrName
type: string
pattern: "^[a-zA-Z0-9-]+$"
description: Optional name or ID of the Key-Value Store for storing videos and media.
behavior: Defines a dedicated storage container for all downloaded media. Useful for persistent archiving beyond dataset retention.
example: "tiktok-videos-archive"

## Example Input
```json
{
  "hashtags": ["fyp", "ai"],
  "profiles": ["sabrina_ramonov", "angus.sewell"],
  "profileScrapeSections": ["videos", "reposts"],
  "profileSorting": "latest",
  "oldestPostDateUnified": "2 days",
  "newestPostDate": "2025-11-04",
  "excludePinnedPosts": true,
  "searchQueries": ["ai", "learn", "agentic rag", "n8n"],
  "searchSection": "/video",
  "maxProfilesPerQuery": 1,
  "resultsPerPage": 10,
  "shouldDownloadVideos": false,
  "shouldDownloadCovers": false,
  "shouldDownloadSubtitles": false,
  "shouldDownloadSlideshowImages": false,
  "videoKvStoreIdOrName": "tiktok-ai-dataset"
}
```
