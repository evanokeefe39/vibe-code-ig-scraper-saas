from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.auth import get_user_model

User = get_user_model()


class InstagramPost(models.Model):
    id = models.TextField(primary_key=True, db_column='id')

    input_inputUrl = models.TextField(db_column='inputUrl')
    type = models.TextField(db_column='type')
    shortCode = models.TextField(db_column='shortCode')
    caption = models.TextField(blank=True, db_column='caption')
    hashtags = JSONField(default=list, blank=True, db_column='hashtags')
    mentions = JSONField(default=list, blank=True, db_column='mentions')
    url = models.TextField(db_column='url')
    commentsCount = models.PositiveBigIntegerField(default=0, db_column='commentsCount')
    firstComment = models.TextField(blank=True, db_column='firstComment')
    latestComments = JSONField(default=list, blank=True, db_column='latestComments')

    dimensionsHeight = models.PositiveIntegerField(db_column='dimensionsHeight')
    dimensionsWidth = models.PositiveIntegerField(db_column='dimensionsWidth')
    displayUrl = models.TextField(db_column='displayUrl')
    images = JSONField(default=list, blank=True, db_column='images')
    videoUrl = models.TextField(blank=True, null=True, db_column='videoUrl')
    audioUrl = models.TextField(blank=True, null=True, db_column='audioUrl')

    likesCount = models.PositiveBigIntegerField(default=0, db_column='likesCount')
    videoPlayCount = models.PositiveBigIntegerField(null=True, blank=True, db_column='videoPlayCount')
    igPlayCount = models.PositiveBigIntegerField(null=True, blank=True, db_column='igPlayCount')
    videoViewCount = models.PositiveBigIntegerField(null=True, blank=True, db_column='videoViewCount')
    videoDuration = models.FloatField(null=True, blank=True, db_column='videoDuration')

    timestamp = models.DateTimeField(db_column='timestamp')

    ownerFullName = models.TextField(blank=True, db_column='ownerFullName')
    ownerUsername = models.TextField(db_column='ownerUsername')
    ownerId = models.TextField(db_column='ownerId')

    productType = models.TextField(blank=True, db_column='productType')
    isSponsored = models.BooleanField(default=False, db_column='isSponsored')

    taggedUsers = JSONField(default=list, blank=True, db_column='taggedUsers')
    childPosts = JSONField(default=list, blank=True, db_column='childPosts')
    musicInfo = JSONField(null=True, blank=True, db_column='musicInfo')

    # ONLY TWO FOREIGN KEYS
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instagram_posts')
    run = models.ForeignKey('Run', on_delete=models.CASCADE, related_name='instagram_posts')

    extracted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'instagram_posts'
        indexes = [
            models.Index(fields=['run']),
            models.Index(fields=['user']),
            models.Index(fields=['run', '-timestamp']),
        ]


class InstagramComment(models.Model):
    id = models.TextField(primary_key=True, db_column='id')

    postUrl = models.TextField(db_column='postUrl')
    commentUrl = models.TextField(blank=True, db_column='commentUrl')
    text = models.TextField(db_column='text')
    ownerUsername = models.TextField(db_column='ownerUsername')
    ownerProfilePicUrl = models.TextField(blank=True, db_column='ownerProfilePicUrl')
    timestamp = models.DateTimeField(db_column='timestamp')
    repliesCount = models.PositiveIntegerField(default=0, db_column='repliesCount')
    replies = JSONField(default=list, blank=True, db_column='replies')
    likesCount = models.PositiveIntegerField(default=0, db_column='likesCount')
    owner = JSONField(default=dict, blank=True, db_column='owner')

    # ONLY TWO FOREIGN KEYS
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='instagram_comments')
    run = models.ForeignKey('Run', on_delete=models.CASCADE, related_name='instagram_comments')

    extracted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'instagram_comments'
        indexes = [
            models.Index(fields=['run']),
            models.Index(fields=['user']),
            models.Index(fields=['postUrl']),
            models.Index(fields=['-timestamp']),
        ]