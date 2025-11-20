from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth import get_user_model

User = get_user_model()

class YouTubeVideo(models.Model):
    id = models.TextField(primary_key=True, db_column='id')

    title = models.TextField(db_column='title')
    translatedTitle = models.TextField(null=True, blank=True, db_column='translatedTitle')
    type = models.TextField(db_column='type')
    url = models.TextField(db_column='url')
    thumbnailUrl = models.TextField(blank=True, db_column='thumbnailUrl')
    viewCount = models.BigIntegerField(null=True, blank=True, db_column='viewCount')
    date = models.DateTimeField(null=True, blank=True, db_column='date')
    likes = models.BigIntegerField(null=True, blank=True, db_column='likes')
    location = models.TextField(blank=True, db_column='location')
    channelName = models.TextField(db_column='channelName')
    channelUrl = models.TextField(db_column='channelUrl')
    channelUsername = models.TextField(blank=True, db_column='channelUsername')
    channelId = models.TextField(db_column='channelId')
    numberOfSubscribers = models.BigIntegerField(null=True, blank=True, db_column='numberOfSubscribers')
    duration = models.TextField(blank=True, db_column='duration')
    commentsCount = models.BigIntegerField(null=True, blank=True, db_column='commentsCount')
    text = models.TextField(blank=True, db_column='text')
    translatedText = models.TextField(blank=True, db_column='translatedText')
    descriptionLinks = JSONField(default=list, blank=True, db_column='descriptionLinks')
    subtitles = JSONField(default=list, blank=True, db_column='subtitles')
    hashtags = JSONField(default=list, blank=True, db_column='hashtags')
    formats = JSONField(default=list, blank=True, db_column='formats')
    commentsTurnedOff = models.BooleanField(default=False, db_column='commentsTurnedOff')
    isMembersOnly = models.BooleanField(default=False, db_column='isMembersOnly')
    isMonetized = models.BooleanField(null=True, blank=True, db_column='isMonetized')
    order = models.IntegerField(null=True, blank=True, db_column='order')
    fromYTUrl = models.TextField(blank=True, db_column='fromYTUrl')
    input = models.TextField(blank=True, db_column='input')
    fromChannelListPage = models.TextField(blank=True, db_column='fromChannelListPage')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='youtube_videos')
    run = models.ForeignKey('Run', on_delete=models.CASCADE, related_name='youtube_videos')
    extracted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'youtube_videos'
        indexes = [
            models.Index(fields=['run']),
            models.Index(fields=['user']),
        ]