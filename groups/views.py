from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView
from rest_framework import permissions
from drf_spectacular.utils import extend_schema

from .models import Group, Like, Tag, UserGroup
from .serializers import GroupSerializer, LikeSerializer, TagSerializer, UserGroupSerializer, TagBatchSerializer
from .helpers import send_invitation_message, get_tags_json

class GroupList(ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def get_queryset(self):
        groups = UserGroup.objects.filter(user_id=self.request.user.id).values_list('group_id', flat=True)
        return Group.objects.filter(id__in=groups)

    def perform_create(self, serializer):
        default_tags_models = Tag.objects.all().filter(id__in=[1, 2, 3])
        default_tags_json = TagSerializer(default_tags_models, many=True).data
        for d in default_tags_json:
            del d['id']

        final_tags_json = self.request.data['tags']
        final_tags_json = default_tags_json + final_tags_json
        self.request.data['tags'] = final_tags_json
        serializer.save(admin_user_id=self.request.user.id)
        group = Group.objects.get(pk=serializer.data['id'])
        UserGroup.objects.create(user_id=self.request.user.id, group=group, admin_approved=True, user_approved=True)
    

class GroupDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def patch(self, request, pk):
        return self.partial_update(request, pk)
        

class GroupTagList(ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.all().filter(group=self.kwargs['pk'])


class GroupUserList(ListAPIView):
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupSerializer

    def get_queryset(self):
        return UserGroup.objects.all().filter(group_id=self.kwargs['gid'], admin_approved=True, user_approved=True)
    
    def list(self, request, *args, **kwargs):
        rsp = super().list(request, *args, **kwargs)
        print(rsp.data)
        items = rsp.data['results'] if 'results' in rsp.data else rsp.data

        print(items)
        for item in items:
            item['tags'] = get_tags_json(request.user.id, item['user']['id'], item['group'])
        return rsp
        

# TODO: detele user from group permission check

class GroupUserDetail(RetrieveUpdateDestroyAPIView, CreateAPIView):
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupSerializer
    lookup_fields = ['uid', 'gid']
    http_method_names = ['get', 'put', 'delete', 'post']

    def get_object(self):
        return get_object_or_404(UserGroup, user_id=self.kwargs['uid'], group_id=self.kwargs['gid'])


    def perform_create(self, serializer):
        group = serializer.group
        print(group)
        if group.allow_without_approval:
            serializer.admin_approved = True
        serializer.save()

    # admin approve user & user accept invitation
    def update(self, request, gid, uid):
        args = {}
        self_uid = request.user.id
        print(self_uid)
        group = Group.objects.get(pk=gid)
        if self_uid == uid:
            args['user_approved'] = True
        elif self_uid == group.admin_user_id:
            args['admin_approved'] = True
        super().update(request, args)

    # get user info in group
    def get(self, request, gid, uid):
        user_group = get_object_or_404(UserGroup, user_id=uid, group_id=gid, admin_approved=True, user_approved=True)
        serializer = self.get_serializer(user_group)

        tags_json = get_tags_json(request.user.id, uid, gid)

        rsp_data = serializer.data
        rsp_data['tags'] = tags_json
        return Response(rsp_data, status=status.HTTP_200_OK)

    # invite user into group
    # TODO: body contains all emails need to be invitations
    def post(self, request, gid, uid):
        self_uid = request.user.id
        from_user_group = UserGroup.objects.filter(user_id=self_uid, group_id=gid)
        to_user_group = UserGroup.objects.filter(user_id=uid, group_id=gid)
        if from_user_group.exists() and not to_user_group.exists():
            to_user_group = UserGroup(user_id=uid, group_id=gid)
            group = Group.objects.get(pk=gid)
            if group.allow_without_approval:
                to_user_group.admin_approved = True
            to_user_group.save()

            send_invitation_message(group, self_uid, uid)
        
        to_user_group = get_object_or_404(UserGroup, user_id=uid, group_id=gid)
        serializer = self.serializer_class(to_user_group)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class LikeDetail(APIView):
    # TODO: req schema
    @extend_schema(
        request=TagBatchSerializer,
        responses=TagSerializer(many=True)
    )
    def put(self, request):
        uid_from = request.data['fromUserId']
        uid_to = request.data['toUserId']
        newTagIds = request.data['tagIds']
        groupId = request.data['groupId']

        oldTagIds = Like.objects.filter(from_user_id=uid_from, to_user_id=uid_to, group_id=groupId).values_list('tag_id', flat=True)
        createTagIds = list(set(newTagIds) - set(oldTagIds))
        deleteTagIds = list(set(oldTagIds) - set(newTagIds))
        for tagId in createTagIds:
            like = Like(from_user_id=uid_from, to_user_id=uid_to, tag_id=tagId, group_id=groupId)
            like.save()
        for tagId in deleteTagIds:
            like = Like.objects.get(from_user_id=uid_from, to_user_id=uid_to, tag_id=tagId, group_id=groupId)
            like.delete()
        return Response(status=status.HTTP_200_OK)


class TagBatch(APIView):
    serializer_class = TagSerializer

    @extend_schema(
        request=TagBatchSerializer,
        responses=TagSerializer(many=True)
    )

    def post(self, request):
        ids = request.data['id']
        tags = Tag.objects.filter(id__in=ids)
        serializer = self.serializer_class(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)