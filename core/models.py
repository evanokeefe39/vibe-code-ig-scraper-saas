from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

class User(AbstractUser):
    # Extend for Supabase integration later
    supabase_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_tier = models.CharField(max_length=50, default='free')

class SocialProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50)  # e.g., 'instagram', 'tiktok'
    profile_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

class Location(models.Model):
    user_id = models.BigIntegerField(null=True)
    mapbox_suggestion = models.CharField(max_length=500)
    mapbox_searched = models.CharField(max_length=500)
    business_name = models.CharField(max_length=255)
    address = models.TextField(null=True)
    vibes = ArrayField(models.CharField(max_length=100))  # Array of strings
    cost_note = models.TextField()
    confidence = models.FloatField()
    post_url = models.TextField()
    profile_url = models.TextField()
    video_url = models.TextField()
    sk = models.CharField(max_length=64, primary_key=True)
    run_id = models.CharField(max_length=255, default='')
    created_at = models.DateTimeField(auto_now_add=True)

class CuratedList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    locations = models.ManyToManyField(Location)
    created_at = models.DateTimeField(auto_now_add=True)
