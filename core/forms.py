import json
from django import forms
from django.forms import formset_factory
from .models import Run

# Grouped choices for source type
SOURCE_TYPE_CHOICES = [
    ('', '🔍 Select Source Type'),
    ('YouTube', [
        ('youtube-search', '🎥 YouTube Search'),
        ('youtube-channel', '📺 YouTube Channel'),
        ('youtube-playlist', '📋 YouTube Playlist'),
        ('youtube-hashtag', '#️⃣ YouTube Hashtag'),
        ('youtube-video', '🎬 YouTube Video'),
    ]),
    ('Instagram', [
        ('instagram-profile', '📷 Instagram Profile'),
        ('instagram-post', '📸 Instagram Post'),
        ('instagram-hashtag', '#️⃣ Instagram Hashtag'),
    ]),
    ('TikTok', [
        ('tiktok-profile', '👤 TikTok Profile'),
        ('tiktok-hashtag', '#️⃣ TikTok Hashtag'),
        ('tiktok-search', '🔍 TikTok Search'),
        ('tiktok-video', '🎵 TikTok Video'),
    ]),
]

class SourceForm(forms.Form):
    """Form for individual source configuration in multi-source scraping"""
    
    source_type = forms.ChoiceField(
        choices=SOURCE_TYPE_CHOICES,
        widget=forms.Select(attrs={
            'class': 'source-type-select w-full px-3 py-2 border border-gray-200 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        })
    )
    
    # Common fields
    max_results = forms.IntegerField(
        initial=50,
        min_value=1,
        max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'max-results-input w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        })
    )
    
    # Platform-specific fields (all present, validation based on source_type)
    search_queries = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'search-queries-textarea w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500',
            'rows': 3,
            'placeholder': 'Enter search terms, one per line'
        })
    )
    profile_urls = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'direct-urls-textarea w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500',
            'rows': 3,
            'placeholder': 'Enter URLs, one per line'
        })
    )
    hashtags = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'hashtags-textarea w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500',
            'rows': 2,
            'placeholder': 'Enter hashtags, one per line'
        })
    )
    channels = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'channels-textarea w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500',
            'rows': 2,
            'placeholder': 'Enter channel names, one per line'
        })
    )
    
    # YouTube-specific fields
    sorting_order = forms.ChoiceField(
        required=False,
        choices=[
            ('relevance', 'Relevance'),
            ('rating', 'Rating'),
            ('date', 'Date'),
            ('views', 'Views'),
        ],
        widget=forms.Select(attrs={
            'class': 'sorting-order-select w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        })
    )
    date_filter = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Any time'),
            ('hour', 'Last hour'),
            ('today', 'Today'),
            ('week', 'This week'),
            ('month', 'This month'),
            ('year', 'This year'),
        ],
        widget=forms.Select(attrs={
            'class': 'date-filter-select w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        })
    )
    video_type = forms.ChoiceField(
        required=False,
        choices=[
            ('video', 'Video'),
            ('movie', 'Movie'),
        ],
        widget=forms.Select(attrs={
            'class': 'video-type-select w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        })
    )
    length_filter = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Any length'),
            ('under4', 'Under 4 minutes'),
            ('between420', '4-20 minutes'),
            ('plus20', 'Over 20 minutes'),
        ],
        widget=forms.Select(attrs={
            'class': 'length-filter-select w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        })
    )
    
    # Quality filters
    is_hd = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'is-hd-checkbox'
        })
    )
    has_subtitles = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'has-subtitles-checkbox'
        })
    )
    has_cc = forms.BooleanField(required=False)
    is_3d = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'is-3d-checkbox'
        })
    )
    is_live = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'is-live-checkbox'
        })
    )
    is_4k = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'is-4k-checkbox'
        })
    )
    is_360 = forms.BooleanField(required=False)
    has_location = forms.BooleanField(required=False)
    is_hdr = forms.BooleanField(required=False)
    is_vr180 = forms.BooleanField(required=False)
    is_bought = forms.BooleanField(required=False)
    
    # Subtitle options
    subtitles_language = forms.ChoiceField(
        required=False,
        choices=[
            ('any', 'Any'),
            ('en', 'English'),
            ('de', 'German'),
            ('es', 'Spanish'),
            ('fr', 'French'),
        ],
        widget=forms.Select(attrs={
            'class': 'subtitles-language-select w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        })
    )
    download_subtitles = forms.BooleanField(required=False)
    prefer_auto_generated_subtitles = forms.BooleanField(required=False)
    save_subs_to_kvs = forms.BooleanField(required=False)
    subtitles_format = forms.ChoiceField(
        required=False,
        choices=[
            ('srt', 'SRT'),
            ('vtt', 'VTT'),
        ],
        widget=forms.Select(attrs={
            'class': 'subtitles-format-select w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        })
    )
    
    # Instagram-specific fields
    feed_type = forms.ChoiceField(
        required=False,
        choices=[
            ('posts', 'Posts only'),
            ('tagged', 'Tagged posts'),
            ('reels', 'Reels only'),
        ],
        widget=forms.Select(attrs={
            'class': 'feed-type-select w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        })
    )
    oldest_post_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'oldest-post-date-input w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500',
            'type': 'date'
        })
    )
    relative_date_filter = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'No filter'),
            ('1 minute', 'Last minute'),
            ('1 hour', 'Last hour'),
            ('1 day', 'Last 24 hours'),
            ('3 days', 'Last 3 days'),
            ('7 days', 'Last 7 days'),
            ('30 days', 'Last 30 days'),
        ],
        widget=forms.Select(attrs={
            'class': 'relative-date-filter-select w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        })
    )
    results_type = forms.ChoiceField(
        required=False,
        choices=[
            ('posts', 'Posts'),
            ('comments', 'Comments'),
            ('mentions', 'Mentions'),
        ],
        widget=forms.Select(attrs={
            'class': 'results-type-select w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        })
    )

# Create formset factory
SourceFormSet = formset_factory(SourceForm, extra=1, can_delete=True)

class RunForm(forms.ModelForm):
    # Multi-source configuration
    sources = forms.JSONField(
        initial=[],
        widget=forms.HiddenInput(),
        help_text="JSON array of sources with platform-specific configurations"
    )
    
    # Global settings
    days_since = forms.IntegerField(
        initial=14,
        min_value=1,
        max_value=365,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        }),
        help_text="Number of days to look back for posts"
    )
    max_results = forms.IntegerField(
        initial=50,
        min_value=1,
        max_value=1000,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        }),
        help_text="Maximum number of posts to process per source"
    )
    
    # Column inference settings
    auto_infer_columns = forms.BooleanField(
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50'
        }),
        help_text="Automatically infer columns from scraped data structure"
    )
    custom_columns = forms.JSONField(
        required=False,
        initial=[],
        widget=forms.HiddenInput(),
        help_text="Custom column definitions (name, type, description)"
    )
    
    # Extraction settings
    enable_extraction = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50'
        }),
        help_text="Enable AI-powered extraction of entities from scraped posts"
    )
    extraction_prompt = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 6,
            'placeholder': 'Describe what data to extract from posts...',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 max-h-40 overflow-y-auto'
        }),
        initial="Extract location information, business mentions, contact details, and other relevant data from social media posts. Adapt to the specific platform and content type.",
        help_text="Custom prompt for AI extraction (leave default for standard data extraction)"
    )

    class Meta:
        model = Run
        fields = []  # Custom form fields, save overridden

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.input:
            # Pre-populate fields from JSON if editing
            data = self.instance.input
            self.fields['sources'].initial = data.get('sources', [])
            self.fields['days_since'].initial = data.get('days_since', 14)
            self.fields['max_results'].initial = data.get('max_results', 50)
            self.fields['auto_infer_columns'].initial = data.get('auto_infer_columns', True)
            self.fields['custom_columns'].initial = data.get('custom_columns', [])
            self.fields['extraction_prompt'].initial = data.get('extraction_prompt', "Extract location information, business mentions, contact details, and other relevant data from social media posts. Adapt to the specific platform and content type.")
            self.fields['enable_extraction'].initial = self.instance.enable_extraction

    def clean_sources(self):
        sources = self.cleaned_data['sources']
        if not sources:
            raise forms.ValidationError("At least one source must be added.")
        
        # Validate each source
        for source in sources:
            if not isinstance(source, dict):
                raise forms.ValidationError("Each source must be a valid configuration.")
            
            source_type = source.get('sourceType')
            config = source.get('config', {})
            
            # Validate source type
            valid_source_types = [
                'youtube-search', 'youtube-channel', 'youtube-playlist', 'youtube-hashtag', 'youtube-video',
                'instagram-profile', 'instagram-post', 'instagram-hashtag', 'instagram-search',
                'tiktok-profile', 'tiktok-hashtag', 'tiktok-search', 'tiktok-video'
            ]
            
            if source_type not in valid_source_types:
                raise forms.ValidationError(f"Invalid source type: {source_type}")
            
            # Validate source type-specific configuration
            if source_type.startswith('youtube-'):
                if source_type == 'youtube-search':
                    if not config.get('searchQueries'):
                        raise forms.ValidationError("YouTube Search source must have search queries.")
                else:
                    # YouTube channel, playlist, hashtag, video need startUrls
                    if not config.get('startUrls'):
                        raise forms.ValidationError(f"{source_type} source must have URLs.")
                        
            elif source_type.startswith('instagram-'):
                if source_type == 'instagram-search':
                    if not config.get('searchQueries'):
                        raise forms.ValidationError("Instagram Search source must have search queries.")
                else:
                    # Instagram profile, post, hashtag need directUrls
                    if not config.get('directUrls'):
                        raise forms.ValidationError(f"{source_type} source must have URLs.")
                        
            elif source_type.startswith('tiktok-'):
                if source_type == 'tiktok-profile':
                    if not config.get('profiles'):
                        raise forms.ValidationError("TikTok Profile source must have profile usernames.")
                elif source_type == 'tiktok-hashtag':
                    if not config.get('hashtags'):
                        raise forms.ValidationError("TikTok Hashtag source must have hashtags.")
                elif source_type == 'tiktok-search':
                    if not config.get('searchQueries'):
                        raise forms.ValidationError("TikTok Search source must have search queries.")
                elif source_type == 'tiktok-video':
                    if not config.get('postURLs'):
                        raise forms.ValidationError("TikTok Video source must have post URLs.")
        
        return sources

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.enable_extraction = self.cleaned_data['enable_extraction']
        instance.input = json.dumps({
            'sources': self.cleaned_data['sources'],
            'days_since': self.cleaned_data['days_since'],
            'max_results': self.cleaned_data['max_results'],
            'auto_infer_columns': self.cleaned_data['auto_infer_columns'],
            'custom_columns': self.cleaned_data['custom_columns'],
            'extraction_prompt': self.cleaned_data['extraction_prompt']
        })
        if commit:
            instance.save()
        return instance