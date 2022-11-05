from django.contrib import admin
from .models import Group

class BaseAdmin(admin.ModelAdmin):
    pass
    # exclude = ('is_deleted', 'deleted_at')



@admin.register(Group)
class GroupAdmin(BaseAdmin):
    pass
