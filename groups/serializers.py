from rest_framework import serializers
from django.contrib.auth.models import User
from drf_writable_nested.serializers import WritableNestedModelSerializer
from rest_framework.parsers import JSONParser

from .models import Group, Tag, Like, UserGroup

import io
import environ
import requests

env = environ.Env()
environ.Env.read_env()

READ_ONLY_FIELDS = ('id', 'created_at', 'updated_at')

class TagSerializer(WritableNestedModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'description', 'icon_id']
        read_only_fields = READ_ONLY_FIELDS

class TagBatchSerializer(serializers.Serializer):
    id = serializers.ListField(child=serializers.IntegerField())


class GroupSerializer(WritableNestedModelSerializer):
    tags = TagSerializer(many=True, partial=True)
    description = serializers.CharField(required=False)
   
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'icon_id', 'allow_without_approval', 'tags', 'admin_user_id', 'created_at', 'updated_at']
        read_only_fields = READ_ONLY_FIELDS + ('admin_user_id',)
    

class GroupBatchSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = READ_ONLY_FIELDS


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']
        read_only_fields = READ_ONLY_FIELDS



class UserGroupSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = UserGroup
        fields = ['user', 'user_approved', 'admin_approved', 'group'] # TODO: post return value is not correct
        read_only_fields = READ_ONLY_FIELDS

    
    def get_user(self, obj):
        user_service = env('USER_SERVICE')
        get_user_path = env('GET_USER_PATH')
        user_url_base = f'{user_service}{get_user_path}/'
        user = requests.get(f'{user_url_base}{obj.user_id}')
        if user.status_code == 200:
            user_json = user.json()['profile']
            user_json['email'] = user.json()['email']
        else:
            user_json = {'userNotExist': True}
        
        return UserSerializer(data=user_json).initial_data
    
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = READ_ONLY_FIELDS


class UserGroupBatchSerializer(serializers.Serializer):
    emails = serializers.ListField(child=serializers.CharField())

class LikePutSerializer(serializers.Serializer):
    uid_from = serializers.IntegerField()
    uid_to = serializers.IntegerField()
    tagIds = serializers.ListField(child=serializers.IntegerField())
    groupId = serializers.IntegerField()