# Model Migration Plan: Current → New Structure

## Overview
Migrate from current Django models to new simplified models defined in `n8n/v2/database-interfaces/`. This is a major structural change that affects all social media data models.

## Key Changes Summary

### 1. Primary Key Changes
- **Current**: `BigAutoField` with `db_column='django_id'` + separate ID field
- **New**: `TextField` primary key using actual platform ID as PK

### 2. Field Naming Convention
- **Current**: Mixed snake_case/camelCase, inconsistent
- **New**: Consistent camelCase for all `db_column` names

### 3. Data Structure Changes
- **Current**: Flattened fields from nested JSON + preserved nested objects
- **New**: Keep nested data as JSON, fewer flattened fields

### 4. Foreign Key Changes
- **Current**: `SET_NULL` on delete for `run` field
- **New**: `CASCADE` on delete for `run` field

### 5. Timestamp Fields
- **Current**: `extraction_date`, `last_updated`, `expires_at`
- **New**: `extracted_at` (auto_now_add)

## Model-by-Model Changes

### YouTubeVideo
**Removed Fields:**
- `video_id` (now primary key)
- `url`, `title` (duplicates)
- `translated_title` → `translatedTitle`
- `description` → `text`
- `thumbnail_url` → `thumbnailUrl`
- `view_count` → `viewCount`
- `like_count` → `likes`
- `comment_count` → `commentsCount`
- `published_at` → `date`
- `duration_seconds` → `duration` (TextField)
- `channel_*` fields → flattened in JSON
- `subscriber_count` → `numberOfSubscribers`
- `text_content` → `text`
- `hashtags` (ArrayField → JSONField)
- `tags` → removed
- `language`, `category` → removed
- `is_monetized` → `isMonetized`
- `comments_disabled` → `commentsTurnedOff`
- `is_members_only` → `isMembersOnly`
- `source_type` → removed
- `extraction_date`, `last_updated`, `expires_at` → `extracted_at`

**Added Fields:**
- `translatedText`, `descriptionLinks`, `formats`, `order`, `fromYTUrl`, `input`, `fromChannelListPage`

### TikTokVideo
**Removed Fields:**
- `tiktok_id` (now primary key)
- All flattened `author_*` fields (now in `authorMeta` JSON)
- All flattened `music_*` fields (now in `musicMeta` JSON)
- `location_created` → removed
- `web_video_url` → `webVideoUrl`
- `video_*` fields → `videoMeta` JSON
- `digg_count` → `diggCount`
- `share_count` → `shareCount`
- `play_count` → `playCount`
- `collect_count` → `collectCount`
- `comment_count` → `commentCount`
- `mentions` (ArrayField → JSONField)
- `is_slideshow` → `isSlideshow`
- `is_pinned` → `isPinned`
- `is_sponsored` → `isSponsored`
- `author_meta`, `music_meta`, `video_meta` → `authorMeta`, `musicMeta`, `videoMeta`
- `subtitle_links` → removed
- `extraction_date`, `last_updated` → `extracted_at`

**Added Fields:**
- `mediaUrls`, `input`, `fromProfileSection`, `submittedVideoUrl`

### InstagramPost
**Removed Fields:**
- `instagram_id` (now primary key)
- `short_code` → `shortCode`
- `hashtags` (ArrayField → JSONField)
- `mentions` (ArrayField → JSONField)
- `comments_count` → `commentsCount`
- `first_comment` → `firstComment`
- `dimensions_height` → `dimensionsHeight`
- `dimensions_width` → `dimensionsWidth`
- `display_url` → `displayUrl`
- `video_url` → `videoUrl`
- `video_view_count` → `videoViewCount`
- `video_play_count` → `videoPlayCount`
- `video_duration` → `videoDuration`
- `likes_count` → `likesCount`
- `owner_full_name` → `ownerFullName`
- `owner_username` → `ownerUsername`
- `owner_id` → `ownerId`
- `product_type` → `productType`
- `music_info` → `musicInfo`
- `input_url` → `input_inputUrl` (naming conflict)
- `child_posts` → `childPosts`
- `tagged_users` → `taggedUsers`
- `is_pinned`, `is_comments_disabled`, `alt`, `audio_url`, `ig_play_count`, `fb_like_count`, `fb_play_count`, `reshare_count` → removed
- `extraction_date`, `last_updated`, `expires_at` → `extracted_at`

**Added Fields:**
- `latestComments`, `audioUrl`, `igPlayCount`, `videoViewCount`

### InstagramComment & InstagramMention
**Removed Models:** These will be removed entirely as mentions are now stored in JSON within InstagramPost.

## Migration Strategy

### Phase 1: Schema Migration
1. Create new migration file with all field changes
2. Handle primary key changes (BigAutoField → TextField)
3. Update foreign key constraints
4. Add new fields, remove old fields
5. Update indexes and table names

### Phase 2: Data Migration
1. **YouTubeVideo**: Transform flattened fields back to JSON structure
2. **TikTokVideo**: Move flattened author/music fields into JSON objects
3. **InstagramPost**: Convert arrays to JSON, restructure data
4. **InstagramComment/InstagramMention**: Migrate data to InstagramPost JSON fields

### Phase 3: Code Updates
1. Update `core/models.py` with new model definitions
2. Update any view logic that references old field names
3. Update templates if they reference old fields
4. Update any JavaScript that processes these fields

### Phase 4: Testing & Validation
1. Test migration on development database
2. Verify data integrity after migration
3. Test application functionality
4. Run existing test suite

## Risk Assessment

### High Risk
- Primary key changes could cause data loss if not handled properly
- Foreign key constraint changes (SET_NULL → CASCADE)
- Complex data transformation for JSON fields

### Medium Risk
- Field name changes breaking existing code
- Index changes affecting query performance
- Table name changes (`core_*` → custom names)

### Low Risk
- Adding new fields (backwards compatible)
- Removing unused fields
- Meta class changes (ordering, indexes)

## Rollback Plan
1. Keep backup of current database schema
2. Create reverse migration if needed
3. Document all changes for potential rollback
4. Test rollback procedure on development

## Success Criteria
- [ ] All existing data preserved during migration
- [ ] No application crashes after migration
- [ ] All existing functionality works
- [ ] New model structure matches `n8n/v2/database-interfaces/`
- [ ] Performance not degraded
- [ ] All tests pass</content>
<parameter name="filePath">C:\Users\evano\repos\vibe-code-ig-scraper-saas\MIGRATION_PLAN.md