from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Group, Tag, Like, UserGroup
from drf_writable_nested.serializers import WritableNestedModelSerializer
import io
from rest_framework.parsers import JSONParser

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
        read_only_fields = READ_ONLY_FIELDS + ('admin_user_id',)
    

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
        user_json = '''
        {
            "id": 1,
            "first_name": "test",
            "last_name": "",
            "email": ""
        }'''
        
        data = JSONParser().parse(io.BytesIO(user_json.encode()))
        data['id'] = obj.user_id
        return UserSerializer(data=data).initial_data
    
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = READ_ONLY_FIELDS