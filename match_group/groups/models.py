from django.db import models
from django_softdelete.models import SoftDeleteModel

class TimeInfo(SoftDeleteModel):
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        abstract = True
        # ordering = ["-updated_at"]


class Group(TimeInfo):
    description = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    admin_user_id = models.IntegerField()
    icon_id = models.IntegerField()
    allow_without_approval = models.BooleanField(default=False)

    
class Tag(TimeInfo):
    name = models.CharField(max_length=100)
    group_id = models.IntegerField()
    description = models.CharField(max_length=100)
    icon_id = models.IntegerField()


class Like(TimeInfo):
    user_id_1 = models.IntegerField()
    user_id_2 = models.IntegerField()
    tag_id = models.IntegerField()
    processed = models.BooleanField(default=False)
    valid = models.BooleanField(default=False)

class UserGroup(TimeInfo):
    user_id = models.IntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)