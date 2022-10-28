from django.test import TestCase
from .models import Group, Tag, Like, UserGroup

class Test(TestCase):
    @classmethod
    def setUpTestData(cls):
        Group.objects.create(description="test group", name="test_group", admin_user_id=1, icon_id=1, allow_without_approval=True)
        Group.objects.create(description="test group 2", name="test_group2", admin_user_id=2, icon_id=1, allow_without_approval=True)
        
        Tag.objects.create(name="test_tag", group_id=1, description="test tag", icon_id=1)

        UserGroup.objects.create(user_id=1, group_id=1, approved=True)
        UserGroup.objects.create(user_id=2, group_id=1, approved=True)
        UserGroup.objects.create(user_id=1, group_id=2, approved=False)

        Like.objects.create(user_id_1=1, user_id_2=2, tag_id=1, processed=True, valid=True)

    def test_get_groups(self):
        groups = UserGroup.objects.filter(user_id=1, approved=True)
        self.assertEqual(len(groups), 1)
