import json
from django import forms
from .models import Run

class RunForm(forms.ModelForm):
    profiles = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter Instagram profile URLs, one per line'}),
        help_text="Enter full Instagram profile URLs (e.g., https://www.instagram.com/username/), one per line."
    )
    days_since = forms.IntegerField(
        initial=14,
        min_value=1,
        max_value=365,
        help_text="Number of days to look back for posts"
    )

    class Meta:
        model = Run
        fields = []  # Custom form fields, save overridden

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.input:
            # Pre-populate fields from JSON if editing
            data = self.instance.input
            self.fields['profiles'].initial = '\n'.join(data.get('profiles', []))
            self.fields['days_since'].initial = data.get('days_since', 14)

    def clean_profiles(self):
        profiles = self.cleaned_data['profiles']
        # Split by lines and strip
        profile_list = [p.strip() for p in profiles.split('\n') if p.strip()]
        # Basic validation
        for profile in profile_list:
            if not profile.startswith('https://www.instagram.com/'):
                raise forms.ValidationError(f"Invalid Instagram URL: {profile}")
        return profile_list

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.input = json.dumps({
            'profiles': self.cleaned_data['profiles'],
            'days_since': self.cleaned_data['days_since']
        })
        if commit:
            instance.save()
        return instance