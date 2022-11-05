from django.contrib import admin
from .models import Group, Tag, Like, UserGroup

class BaseAdmin(admin.ModelAdmin):
    # pass
    exclude = ('is_deleted', 'deleted_at')



@admin.register(Group)
class GroupAdmin(BaseAdmin):
    pass

@admin.register(Tag)
class GroupAdmin(BaseAdmin):
    pass

@admin.register(Like)
class GroupAdmin(BaseAdmin):
    pass

@admin.register(UserGroup)
class GroupAdmin(BaseAdmin):
    pass

    