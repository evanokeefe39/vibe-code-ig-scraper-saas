# Platform Configuration Requirements

This document captures the complete configuration requirements for all 14 platform types in the scraper.

## YouTube Platform

### YouTube Search (`youtube-search`)
**Cost**: $5.00 per 1000 results

**Required Fields**:
- `search_queries` - Search terms like typing in YouTube's search bar

**Optional Fields**:
- `sorting_order` - Sorting order dropdown
- `date_filter` - Date filter dropdown  
- `video_type` - Video type dropdown
- `length_filter` - Length filter dropdown
- `max_results` - Max videos (default: 50)

**Quality Filters**:
- `is_hd` - HD checkbox
- `has_subtitles` - Has Subtitles checkbox
- `is_3d` - 3D checkbox
- `is_live` - Live checkbox
- `is_4k` - 4K checkbox

**Subtitle Options**:
- `subtitles_language` - Subtitle language dropdown
- `download_subtitles` - Download Subtitles checkbox
- `prefer_auto_generated_subtitles` - Prefer Auto-Generated checkbox

### YouTube Channel (`youtube-channel`)
**Cost**: $5.00 per 1000 results

**Required Fields**:
- `profile_urls` - YouTube channel URLs, one per line

**Optional Fields**:
- `sorting_order` - Video sorting dropdown
- `oldest_post_date` - Oldest post date input
- `relative_date_filter` - Relative date filter dropdown
- `max_results` - Max videos (default: 50)
- `max_results_shorts` - Max shorts (default: 10) - **Custom HTML Input**
- `max_results_streams` - Max streams (default: 5) - **Custom HTML Input**

**Subtitle Options**:
- `subtitles_language` - Subtitle language dropdown
- `download_subtitles` - Download Subtitles checkbox
- `prefer_auto_generated_subtitles` - Prefer Auto-Generated checkbox

### YouTube Playlist (`youtube-playlist`)
**Cost**: $5.00 per 1000 results

**Required Fields**:
- `profile_urls` - YouTube playlist URLs, one per line

**Optional Fields**:
- `max_results` - Max videos (default: 50)

**Subtitle Options**:
- `subtitles_language` - Subtitle language dropdown
- `download_subtitles` - Download Subtitles checkbox
- `prefer_auto_generated_subtitles` - Prefer Auto-Generated checkbox

### YouTube Hashtag (`youtube-hashtag`)
**Cost**: $5.00 per 1000 results

**Required Fields**:
- `hashtags` - Hashtags without # symbol, one per line

**Optional Fields**:
- `max_results` - Max videos per hashtag (default: 50)

**Subtitle Options**:
- `subtitles_language` - Subtitle language dropdown
- `download_subtitles` - Download Subtitles checkbox
- `prefer_auto_generated_subtitles` - Prefer Auto-Generated checkbox

### YouTube Video (`youtube-video`)
**Cost**: $5.00 per 1000 results

**Required Fields**:
- `profile_urls` - YouTube video URLs, one per line

**Optional Fields**:
- `max_results` - Maximum videos (default: 50)

**Subtitle Options**:
- `subtitles_language` - Subtitle language dropdown
- `download_subtitles` - Download Subtitles checkbox
- `prefer_auto_generated_subtitles` - Prefer Auto-Generated checkbox

## Instagram Platform

### Instagram Profile (`instagram-profile`)
**Cost**: $2.70 per 1000 results

**Required Fields**:
- `profile_urls` - Instagram profile URLs, one per line

**Optional Fields**:
- `feed_type` - Feed options dropdown
- `oldest_post_date` - Oldest post date input
- `relative_date_filter` - Relative date filter dropdown
- `max_results` - Maximum results per profile (default: 50)
- `results_type` - Data type to extract dropdown

### Instagram Post (`instagram-post`)
**Cost**: $2.70 per 1000 results

**Required Fields**:
- `profile_urls` - Instagram post URLs, one per line

**Optional Fields**:
- `max_results` - Maximum results per post (default: 50)
- `oldest_post_date` - Oldest post date input

### Instagram Hashtag (`instagram-hashtag`)
**Cost**: $2.70 per 1000 results

**Required Fields**:
- `profile_urls` - Instagram hashtag URLs, one per line

**Optional Fields**:
- `max_results` - Maximum results per hashtag (default: 50)
- `oldest_post_date` - Oldest post date input

### Instagram Search (`instagram-search`)
**Cost**: $2.70 per 1000 results

**NOTE**: This source type is currently hidden from the UI and not available for selection.

**Required Fields**:
- `search_queries` - Search terms, one per line

**Optional Fields**:
- `search_type` - **Custom HTML Input** - Search type dropdown (hashtag/user/place)
- `search_limit` - **Custom HTML Input** - Search limit (max 250, default: 10)
- `max_results` - Maximum results per search result (default: 50)

## TikTok Platform

### TikTok Profile (`tiktok-profile`)
**Cost**: $5.00 per 1000 results

**Required Fields**:
- `profile_urls` - TikTok profile URLs, one per line

**Optional Fields**:
- `profile_scrape_sections` - **Custom HTML Input** - Profile sections dropdown (videos/reposts/videos,reposts)
- `exclude_pinned_posts` - **Custom HTML Input** - Exclude pinned posts checkbox
- `profile_sorting` - **Custom HTML Input** - Profile sorting dropdown (latest/popular/oldest)
- `oldest_post_date` - Oldest post date input
- `relative_date_filter` - **Custom HTML Input** - Relative date filter dropdown
- `max_results` - Maximum videos per profile (default: 50)
- `newest_post_date` - **Custom HTML Input** - Newest post date input

**Download Options** - **All Custom HTML Inputs**:
- `download_video` - Download Videos checkbox
- `download_covers` - Download Covers checkbox
- `download_subtitles` - Download Subtitles checkbox
- `download_slideshow` - Download Slideshow Images checkbox

### TikTok Hashtag (`tiktok-hashtag`)
**Cost**: $5.00 per 1000 results

**Required Fields**:
- `hashtags` - Hashtags without # symbol, one per line

**Optional Fields**:
- `hashtag_sorting` - **Custom HTML Input** - Hashtag sorting dropdown (latest/popular/oldest)
- `oldest_post_date` - Oldest post date input
- `relative_date_filter` - **Custom HTML Input** - Relative date filter dropdown
- `max_results` - Maximum videos per hashtag (default: 50)
- `newest_post_date` - **Custom HTML Input** - Newest post date input

**Download Options** - **All Custom HTML Inputs**:
- `download_video` - Download Videos checkbox
- `download_covers` - Download Covers checkbox
- `download_subtitles` - Download Subtitles checkbox
- `download_slideshow` - Download Slideshow Images checkbox

### TikTok Search (`tiktok-search`)
**Cost**: $5.00 per 1000 results

**Required Fields**:
- `search_queries` - Search terms, one per line

**Optional Fields**:
- `search_type` - **Custom HTML Input** - Search type dropdown (top/user/video/hashtag/live)
- `search_sorting` - **Custom HTML Input** - Search sorting dropdown (relevance/latest/popular)
- `oldest_post_date` - Oldest post date input
- `relative_date_filter` - **Custom HTML Input** - Relative date filter dropdown
- `max_results` - Maximum videos per search query (default: 50)
- `newest_post_date` - **Custom HTML Input** - Newest post date input

**Download Options** - **All Custom HTML Inputs**:
- `download_video` - Download Videos checkbox
- `download_covers` - Download Covers checkbox
- `download_subtitles` - Download Subtitles checkbox
- `download_slideshow` - Download Slideshow Images checkbox

### TikTok Video (`tiktok-video`)
**Cost**: $5.00 per 1000 results

**Required Fields**:
- `profile_urls` - TikTok video URLs, one per line

**Download Options** - **All Custom HTML Inputs**:
- `download_video` - Download Videos checkbox (checked by default)
- `download_covers` - Download Covers checkbox
- `download_subtitles` - Download Subtitles checkbox
- `download_slideshow` - Download Slideshow Images checkbox

## Configuration Issues Found

### Critical Issues to Fix:
1. **YouTube Search**: Missing quality filter options in form (is_hd, has_subtitles, is_3d, is_live, is_4k) - FIXED: Added widget attributes
2. **TikTok Hashtag**: Has date filtering (oldest_post_date, relative_date_filter, newest_post_date) but shouldn't according to requirements
3. **TikTok Search**: Has date filtering (oldest_post_date, relative_date_filter, newest_post_date) but shouldn't according to requirements  
4. **TikTok Video**: Missing max_results parameter - FIXED: max_results field already exists as common field

### Custom HTML Inputs (Not Django Form Fields):
These inputs are implemented as plain HTML inputs rather than Django form fields:

**YouTube Channel**:
- `max_results_shorts` - number input
- `max_results_streams` - number input

**Instagram Search**:
- `search_type` - select dropdown
- `search_limit` - number input

**TikTok Profile**:
- `profile_scrape_sections` - select dropdown
- `exclude_pinned_posts` - checkbox
- `profile_sorting` - select dropdown
- `relative_date_filter` - select dropdown
- `newest_post_date` - date input
- All download option checkboxes

**TikTok Hashtag**:
- `hashtag_sorting` - select dropdown
- `relative_date_filter` - select dropdown
- `newest_post_date` - date input
- All download option checkboxes

**TikTok Search**:
- `search_type` - select dropdown
- `search_sorting` - select dropdown
- `relative_date_filter` - select dropdown
- `newest_post_date` - date input
- All download option checkboxes

**TikTok Video**:
- All download option checkboxes

## Form Field Mappings

All Django form fields use the following CSS classes:
- `source-type-select` - Source type dropdown
- `max-results-input` - Max results number input
- `search_queries` - Search queries textarea
- `profile_urls` - Profile URLs textarea
- `hashtags` - Hashtags textarea
- `sorting_order` - Sorting order dropdown
- `date_filter` - Date filter dropdown
- `video_type` - Video type dropdown
- `length_filter` - Length filter dropdown
- `is_hd`, `has_subtitles`, `is_3d`, `is_live`, `is_4k` - Quality filter checkboxes
- `subtitles_language` - Subtitle language dropdown
- `download_subtitles` - Download subtitles checkbox
- `prefer_auto_generated_subtitles` - Prefer auto-generated subtitles checkbox
- `feed_type` - Feed type dropdown
- `oldest_post_date` - Oldest post date input
- `relative_date_filter` - Relative date filter dropdown
- `results_type` - Results type dropdown