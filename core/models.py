from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    # Extend for Supabase integration later
    supabase_id = models.CharField(max_length=255, blank=True, null=True)
    subscription_tier = models.CharField(max_length=50, default='free')

class SocialProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    platform = models.CharField(max_length=50)  # e.g., 'instagram', 'tiktok'
    profile_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

class Run(models.Model):
    user_id = models.BigIntegerField(null=True)
    n8n_execution_id = models.BigIntegerField(blank=True, null=True, db_index=True)
    input = models.JSONField(null=True)  # Scraping parameters (URLs, extraction specs, etc.)
    output = models.JSONField(null=True)  # Extracted data (locations, leads, etc. - flexible schema)
    created_at = models.DateTimeField(auto_now_add=True)



class CuratedList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    data_schema = models.JSONField(null=True, blank=True)  # Optional schema definition for the curated data
    created_at = models.DateTimeField(auto_now_add=True)
