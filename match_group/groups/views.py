from email.policy import HTTP

from django.db.models import Q
from django.shortcuts import render
from rest_framework import generics, mixins, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView

from .models import Group, Like, Tag, UserGroup
from .pagination import Pagination
from .serializers import GroupSerializer, LikeSerializer, TagSerializer, UserGroupSerializer


class GroupList(ListCreateAPIView):
    # paginator = Pagination
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    
# TODO: on cascade delete not working
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
    def get(self, request, gid):
        users = UserGroup.objects.all().filter(group_id=gid, admin_approved=True, user_approved=True).values_list('user_id', flat=True)
        # paginator = Pagination()
        result_page = paginator.paginate_queryset(users, request)
        # serializer = UserSerializer(users, many=True)
        return Response(result_page, status=status.HTTP_200_OK)


class GroupUserDetail(APIView):
    def get(self, request, gid, uid):
        self_uid = request.headers['uid']
        likes = Like.objects.all().filter(user_id_from=self_uid, user_id_to=uid, group_id=gid).values_list('tag_id', flat=True)
        rev_likes = Like.objects.all().filter(user_id_from=uid, user_id_to=self_uid, group_id=gid).values_list('tag_id', flat=True)
        matches = {}
        for tag_id in likes:
            if tag_id in rev_likes:
                matches[tag_id] = True
            else:
                matches[tag_id] = False

        return Response(matches, status=status.HTTP_200_OK)

    def post(self, request, gid, uid):
        if not UserGroup.objects.filter(user_id=uid, group_id=gid).exists():
            user_group = UserGroup(user_id=uid, group_id=gid)
            group = Group.objects.get(pk=gid)
            if group.allow_without_approval:
                user_group.admin_approved = True
            user_group.save()
        return Response(status=status.HTTP_200_OK)
    
    def delete(self, request, gid, uid):
        user_group = UserGroup.objects.get(user_id=uid, group_id=gid)
        user_group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def put(self, request, gid, uid):
        self_uid = request.headers['uid']
        print(self_uid)
        user_group = UserGroup.objects.get(user_id=uid, group_id=gid)
        group = Group.objects.get(pk=gid)
        if self_uid == uid:
            user_group.user_approved = True
        elif self_uid == group.admin_user_id:
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