import json
from django import forms
from .models import Run

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
            
            platform = source.get('platform')
            if platform not in ['instagram', 'tiktok', 'youtube']:
                raise forms.ValidationError(f"Invalid platform: {platform}")
            
            # Get platform-specific configuration
            config = source.get('configuration', {})
            
            # Validate platform-specific configuration
            if platform == 'instagram':
                # Instagram needs either directUrls or search
                if not any([
                    config.get('directUrls'),
                    config.get('search')
                ]):
                    raise forms.ValidationError("Instagram source must have either direct URLs or search terms.")
            elif platform == 'tiktok':
                # TikTok needs at least one of: profiles, hashtags, searchQueries, or postURLs
                if not any([
                    config.get('profiles'),
                    config.get('hashtags'),
                    config.get('searchQueries'),
                    config.get('postURLs')
                ]):
                    raise forms.ValidationError("TikTok source must have at least one of: profiles, hashtags, search queries, or post URLs.")
            elif platform == 'youtube':
                # YouTube needs startUrls (channel URLs)
                if not config.get('startUrls'):
                    raise forms.ValidationError("YouTube source must have at least one channel URL.")
        
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