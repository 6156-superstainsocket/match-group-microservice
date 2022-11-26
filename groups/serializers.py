from rest_framework import serializers
from .models import Group, Tag, Like, UserGroup
from drf_writable_nested.serializers import WritableNestedModelSerializer

READ_ONLY_FIELDS = ('id', 'created_at', 'updated_at')

class TagSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'description', 'icon_id']
        read_only_fields = READ_ONLY_FIELDS


class GroupSerializer(WritableNestedModelSerializer):
    tags = TagSerializer(many=True, partial=True)
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'icon_id', 'allow_without_approval', 'tags', 'admin_user_id']
        read_only_fields = READ_ONLY_FIELDS
    

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = READ_ONLY_FIELDS

class UserGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGroup
        fields = ['user_id']
        read_only_fields = READ_ONLY_FIELDS