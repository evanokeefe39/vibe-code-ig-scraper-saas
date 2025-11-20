from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth import get_user_model

User = get_user_model()


class TikTokVideo(models.Model):
    id = models.TextField(primary_key=True, db_column='id')

    text = models.TextField(blank=True, db_column='text')
    textLanguage = models.TextField(blank=True, db_column='textLanguage')
    createTime = models.BigIntegerField(null=True, blank=True, db_column='createTime')
    createTimeISO = models.DateTimeField(null=True, blank=True, db_column='createTimeISO')
    isAd = models.BooleanField(default=False, db_column='isAd')

    authorMeta = JSONField(default=dict, blank=True, db_column='authorMeta')
    musicMeta = JSONField(default=dict, blank=True, db_column='musicMeta')

    webVideoUrl = models.TextField(db_column='webVideoUrl')
    mediaUrls = JSONField(default=list, blank=True, db_column='mediaUrls')
    videoMeta = JSONField(default=dict, blank=True, db_column='videoMeta')

    diggCount = models.PositiveBigIntegerField(default=0, db_column='diggCount')
    shareCount = models.PositiveBigIntegerField(default=0, db_column='shareCount')
    playCount = models.PositiveBigIntegerField(default=0, db_column='playCount')
    collectCount = models.PositiveBigIntegerField(default=0, db_column='collectCount')
    commentCount = models.PositiveBigIntegerField(default=0, db_column='commentCount')

    mentions = JSONField(default=list, blank=True, db_column='mentions')
    detailedMentions = JSONField(default=list, blank=True, db_column='detailedMentions')
    hashtags = JSONField(default=list, blank=True, db_column='hashtags')
    effectStickers = JSONField(default=list, blank=True, db_column='effectStickers')

    isSlideshow = models.BooleanField(default=False, db_column='isSlideshow')
    isPinned = models.BooleanField(default=False, db_column='isPinned')
    isSponsored = models.BooleanField(default=False, db_column='isSponsored')

    input = models.TextField(blank=True, db_column='input')
    fromProfileSection = models.TextField(blank=True, db_column='fromProfileSection')
    submittedVideoUrl = models.TextField(blank=True, db_column='submittedVideoUrl')

    # ONLY TWO FOREIGN KEYS
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tiktok_videos')
    run = models.ForeignKey('Run', on_delete=models.CASCADE, related_name='tiktok_videos')

    extracted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'tiktok_videos'
        indexes = [
            models.Index(fields=['run']),
            models.Index(fields=['user']),
            models.Index(fields=['run', '-createTimeISO']),
        ]

    def __str__(self):
        return f"TikTok {self.id}"