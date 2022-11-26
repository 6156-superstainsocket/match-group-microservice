from django.contrib import admin
from .models import Group, Tag, Like, UserGroup


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    pass

@admin.register(Tag)
class GroupAdmin(admin.ModelAdmin):
    pass

@admin.register(Like)
class GroupAdmin(admin.ModelAdmin):
    pass

@admin.register(UserGroup)
class GroupAdmin(admin.ModelAdmin):
    pass

    