from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView, CreateAPIView

from .models import Group, Like, Tag, UserGroup
from .serializers import GroupSerializer, LikeSerializer, TagSerializer, UserGroupSerializer


class GroupList(ListCreateAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
# TODO: on cascade delete not working
# TODO: add user to the group when create
# TODO: add default tag when create
class GroupDetail(RetrieveUpdateDestroyAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

    def patch(self, request, pk):
        return self.partial_update(request, pk)
        

class GroupTagList(ListAPIView):
    serializer_class = TagSerializer

    def get_queryset(self):
        return Tag.objects.all().filter(group=self.kwargs['pk'])


class GroupUserList(ListAPIView):
    queryset = UserGroup.objects.all()
    serializer_class = UserGroupSerializer

    def get_queryset(self):
        return UserGroup.objects.all().filter(group_id=self.kwargs['gid'], admin_approved=True, user_approved=True)
        

# # TODO: detele user from group permission check
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
        self_uid = request.headers['uid']
        print(self_uid)
        group = Group.objects.get(pk=gid)
        if self_uid == uid:
            args['user_approved'] = True
        elif self_uid == group.admin_user_id:
            args['admin_approved'] = True
        super().update(request, args)

    # get user info in group
    def get(self, request, gid, uid):
        self_uid = request.headers['uid']
        user = get_object_or_404(UserGroup, user_id=uid, group_id=gid, admin_approved=True, user_approved=True)
        serializer = self.get_serializer(user)
        uid = user.id

        likes = Like.objects.all().filter(user_id_from=self_uid, user_id_to=uid, group_id=gid).values_list('tag_id', flat=True)
        rev_likes = Like.objects.all().filter(user_id_from=uid, user_id_to=self_uid, group_id=gid).values_list('tag_id', flat=True)
        matches = [id for id in likes if id in rev_likes]

        rsp_data = serializer.data
        rsp_data['match_tag_ids'] = matches
        return Response(rsp_data, status=status.HTTP_200_OK)

    # invite user into group
    def post(self, request, gid, uid):
        if not UserGroup.objects.filter(user_id=uid, group_id=gid).exists():
            user_group = UserGroup(user_id=uid, group_id=gid)
            group = Group.objects.get(pk=gid)
            if group.allow_without_approval:
                user_group.admin_approved = True
            user_group.save()
        return Response(status=status.HTTP_200_OK)


class LikeDetail(APIView):
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