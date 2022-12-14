from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class TimeInfo(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    class Meta:
        abstract = True

class Group(TimeInfo):
    description = models.CharField(max_length=100, blank=True, default="", editable=True)
    name = models.CharField(max_length=100)
    admin_user_id = models.IntegerField()
    icon_id = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(31)])
    allow_without_approval = models.BooleanField(default=False)

    
class Tag(TimeInfo):
    name = models.CharField(max_length=100)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='tags')
    description = models.CharField(max_length=100)
    icon_id = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(23)])


class Like(TimeInfo):
    user_id_from = models.IntegerField()
    user_id_to = models.IntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    processed = models.BooleanField(default=False)


class UserGroup(TimeInfo):
    user_id = models.IntegerField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user_approved = models.BooleanField(default=False)
    admin_approved = models.BooleanField(default=False)

    @property
    def uid(self):
        return self.user_id
    
    @property
    def gid(self):
        return self.group.id