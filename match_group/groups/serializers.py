from rest_framework import serializers
from .models import Group, Tag, Like
from drf_writable_nested.serializers import WritableNestedModelSerializer
# from drf_writable_nested import WritableNestedModelSerializer

READ_ONLY_FIELDS = ('id', 'created_at', 'updated_at', 'deleted_at')

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'description', 'icon_id']
        read_only_fields = READ_ONLY_FIELDS


class GroupSerializer(serializers.WritableNestedModelSerializer):
    tags = TagSerializer(many=True, partial=True)
    class Meta:
        model = Group
        fields = ['id', 'name', 'description', 'icon_id', 'allow_without_approval', 'tags', 'admin_user_id']
        read_only_fields = READ_ONLY_FIELDS
    
    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        group = Group.objects.create(**validated_data)
        for tag_data in tags_data:
            Tag.objects.create(group=group, **tag_data)
        return group

    def partial_update(self, instance, validated_data):
        tags_data = validated_data.pop('tags')
        # print(tags_data)
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description', instance.description)
        instance.icon_id = validated_data.get('icon_id', instance.icon_id)
        instance.allow_without_approval = validated_data.get('allow_without_approval', instance.allow_without_approval)
        instance.save()

        old_tags_ids = [tag.id for tag in instance.tags.all()]
        cur_tags_ids = [tag_data.get('id') for tag_data in tags_data] #TODO: can not get id from json data
        to_delete_tags_ids = list(set(old_tags_ids) - set(cur_tags_ids))

        print('old_tags_ids', old_tags_ids)
        print('cur_tags_ids', cur_tags_ids)

        # delete tags
        for tag_id in to_delete_tags_ids:
            Tag.objects.get(id=tag_id).delete()

        # update or create tags
        for tag_data in tags_data:
            print(type(tag_data))
            print(tag_data)
            print('id' in tag_data)
            if 'id' in tag_data: # update
                Tag.objects.get(id=tag_data.get('id')).update(tag_data)
                # print('update')
            else: # create
                Tag.objects.create(group=instance, **tag_data)
                # print('create')
        return instance


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = READ_ONLY_FIELDS