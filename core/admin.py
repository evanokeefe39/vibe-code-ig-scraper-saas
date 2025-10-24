from django.contrib import admin
from .models import User, SocialProfile, Run, CuratedList, CuratedItem

# Register your models here.
admin.site.register(User)
admin.site.register(SocialProfile)
admin.site.register(Run)
admin.site.register(CuratedList)
admin.site.register(CuratedItem)
