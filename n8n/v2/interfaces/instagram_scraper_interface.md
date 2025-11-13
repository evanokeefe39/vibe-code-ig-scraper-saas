# Actor Metadata
title: Instagram Scraper
description: Scrapes and downloads Instagram posts, profiles, hashtags, comments, and metadata based on direct URLs or search queries.
version: 0.0
build_id: 45BDZt2ps4H7n9H1T

## Parameters

### directUrls
type: array[string]
description: List of Instagram URLs to scrape (profiles, posts, hashtags, or places). Either this or `search` must be provided.
behavior: When provided, the scraper runs directly on these URLs. Each URL is processed independently.
example: ["https://www.instagram.com/sabrina_ramonov/", "https://www.instagram.com/p/Cx5abc123/"]

### resultsType
type: string
enum: ["posts", "comments", "details", "mentions", "stories"]
default: "posts"
description: Determines what type of data is extracted from each page.
behavior: 
- `posts`: Scrapes post content (captions, media URLs, engagement metrics).
- `comments`: Extracts comments from individual post URLs.
- `details`: Retrieves metadata for profiles, hashtags, or places.
- `mentions`: Finds posts mentioning the profile or tag.
- `stories`: Scrapes stories from profile URLs (if available).

### resultsLimit
type: integer
minimum: 1
description: Maximum number of items (posts, comments, etc.) to scrape per URL.
behavior: Limits the number of results returned for each target. For posts, caps total posts; for comments, caps total comments per post.
example: 200

### onlyPostsNewerThan
type: string
pattern: "^(\\d{4})-(0[1-9]|1[0-2])-(0[1-9]|[12]\\d|3[01])(T[0-2]\\d:[0-5]\\d(:[0-5]\\d)?(\\.\\d+)?Z?)?$|^(\\d+)\\s*(minute|hour|day|week|month|year)s?$"
description: Temporal filter defining the oldest acceptable post date. Accepts absolute dates (YYYY-MM-DD) or relative durations (e.g. "3 days", "2 months").
behavior: Filters posts or comments to include only those newer than the specified time window.
example: "7 days"

### isUserTaggedFeedURL
type: boolean
description: When true, scrapes the posts a user is tagged in.
behavior: The scraper navigates to the "tagged" tab on each profile instead of the main feed.
example: false

### isUserReelFeedURL
type: boolean
description: When true, scrapes the user's Reels posts.
behavior: The scraper fetches only the "Reels" section of each provided profile.
example: false

### search
type: string
description: Query string for searching Instagram (used if no `directUrls` provided).
behavior: Enables search-based scraping. The scraper will perform a search by `searchType` and process results up to `searchLimit`.
example: "ai startup marketing"

### searchType
type: string
enum: ["user", "hashtag", "place"]
default: "hashtag"
description: Type of search to perform when using the `search` field.
behavior:
- `user`: Finds profiles matching the search query.
- `hashtag`: Finds hashtags matching the query.
- `place`: Finds location pages.
example: "user"

### searchLimit
type: integer
minimum: 1
maximum: 250
description: Maximum number of search results (profiles, hashtags, or places) to scrape.
behavior: Controls how many search results from `searchType` will be processed. Each result is then treated as a `directUrl`.
example: 10

### enhanceUserSearchWithFacebookPage
type: boolean
description: Enhances user search results by fetching linked Facebook Pages and public emails.
behavior: Enables deep data extraction for top 10 users. Increases processing time and cost. May include personal data — ensure compliance.
example: false

### addParentData
type: boolean
default: false
description: Adds metadata about the parent source (profile, hashtag, etc.) to each scraped item.
behavior: Appends contextual fields such as source type, name, and link to results.
example: false

## Example Input
```json
{
  "directUrls": ["https://www.instagram.com/sabrina_ramonov/"],
  "resultsType": "posts",
  "resultsLimit": 100,
  "onlyPostsNewerThan": "1 week",
  "isUserTaggedFeedURL": false,
  "isUserReelFeedURL": false,
  "search": "ai art",
  "searchType": "hashtag",
  "searchLimit": 5,
  "enhanceUserSearchWithFacebookPage": false,
  "addParentData": true
}
```
