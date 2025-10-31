import json
from django import forms
from .models import Run

class RunForm(forms.ModelForm):
    PLATFORM_CHOICES = [
        ('instagram', 'Instagram'),
        ('tiktok', 'TikTok'),
    ]

    platform = forms.ChoiceField(
        choices=PLATFORM_CHOICES,
        initial='instagram',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500'
        }),
        help_text="Select the social media platform to scrape"
    )

    profiles = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 8,
            'placeholder': 'Enter profile URLs, one per line or comma-separated',
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary-500 focus:border-primary-500 max-h-40 overflow-y-auto'
        }),
        help_text="Enter full profile URLs (e.g., https://www.instagram.com/username/ or https://www.tiktok.com/@username), one per line or comma-separated."
    )
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
        help_text="Maximum number of posts to process per profile"
    )
    include_comments = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50'
        }),
        help_text="Include comments in the extraction"
    )
    include_stories = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'rounded border-gray-300 text-primary-600 shadow-sm focus:border-primary-300 focus:ring focus:ring-primary-200 focus:ring-opacity-50'
        }),
        help_text="Include stories in the extraction (if available)"
    )
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
        initial="Extract location information, business mentions, and contact details from social media posts.",
        help_text="Custom prompt for AI extraction (leave default for standard location/business data)"
    )

    class Meta:
        model = Run
        fields = []  # Custom form fields, save overridden

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.input:
            # Pre-populate fields from JSON if editing
            data = self.instance.input
            self.fields['platform'].initial = data.get('platform', 'instagram')
            self.fields['profiles'].initial = '\n'.join(data.get('profiles', []))
            self.fields['days_since'].initial = data.get('days_since', 14)
            self.fields['max_results'].initial = data.get('max_results', 50)
            # self.fields['include_comments'].initial = data.get('include_comments', True)  # Hidden for now
            # self.fields['include_stories'].initial = data.get('include_stories', False)   # Hidden for now
            self.fields['extraction_prompt'].initial = data.get('extraction_prompt', "Extract location information, business mentions, and contact details from social media posts.")
            self.fields['enable_extraction'].initial = self.instance.enable_extraction

    def clean_profiles(self):
        profiles = self.cleaned_data['profiles']
        platform = self.cleaned_data.get('platform', 'instagram')
        # Split by lines or commas and strip
        if '\n' in profiles:
            profile_list = [p.strip() for p in profiles.split('\n') if p.strip()]
        else:
            profile_list = [p.strip() for p in profiles.split(',') if p.strip()]
        # Basic validation based on platform
        expected_prefix = {
            'instagram': 'https://www.instagram.com/',
            'tiktok': 'https://www.tiktok.com/'
        }.get(platform, 'https://www.instagram.com/')

        for profile in profile_list:
            if not profile.startswith(expected_prefix):
                raise forms.ValidationError(f"Invalid {platform.title()} URL: {profile}")
        return profile_list

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.enable_extraction = self.cleaned_data['enable_extraction']
        instance.input = json.dumps({
            'platform': self.cleaned_data['platform'],
            'profiles': self.cleaned_data['profiles'],
            'days_since': self.cleaned_data['days_since'],
            'max_results': self.cleaned_data['max_results'],
            # 'include_comments': self.cleaned_data['include_comments'],  # Hidden for now
            # 'include_stories': self.cleaned_data['include_stories'],    # Hidden for now
            'extraction_prompt': self.cleaned_data['extraction_prompt']
        })
        if commit:
            instance.save()
        return instance