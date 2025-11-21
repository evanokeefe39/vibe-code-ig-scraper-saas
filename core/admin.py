from django.contrib import admin
from .models import User, Run, UserList, ListColumn, ListRow

# Register your models here.
admin.site.register(User)
admin.site.register(Run)
admin.site.register(UserList)
admin.site.register(ListColumn)
admin.site.register(ListRow)
