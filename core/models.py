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
    enable_extraction = models.BooleanField(default=True, help_text="Whether to run LLM extraction on scraped data")
    scraped = models.JSONField(null=True, help_text="Raw scraped data organized by platform: {'instagram': [...], 'tiktok': [...], ...}")
    extracted = models.JSONField(null=True, help_text="Processed entities extracted from scraped data")
    # Keep output temporarily for backward compatibility
    output = models.JSONField(null=True)  # DEPRECATED: Will be removed after migration
    created_at = models.DateTimeField(auto_now_add=True)



class UserList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User List"
        verbose_name_plural = "User Lists"


class ListColumn(models.Model):
    COLUMN_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('date', 'Date'),
        ('boolean', 'Boolean'),
        ('select', 'Select'),
        ('multi_select', 'Multi Select'),
        ('url', 'URL'),
        ('json', 'JSON'),
    ]

    user_list = models.ForeignKey(UserList, on_delete=models.CASCADE, related_name='columns')
    name = models.CharField(max_length=255)
    column_type = models.CharField(max_length=20, choices=COLUMN_TYPES, default='text')
    description = models.TextField(blank=True, help_text="Optional description of what this column contains")
    required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    options = models.JSONField(null=True, blank=True)  # For select/multi_select options
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', 'created_at']
        unique_together = ['user_list', 'name']

    def __str__(self):
        return f"{self.user_list.name} - {self.name} ({self.column_type})"


class ListRow(models.Model):
    user_list = models.ForeignKey(UserList, on_delete=models.CASCADE, related_name='rows')
    data = models.JSONField()  # Stores the row data as JSON
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
