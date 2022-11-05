from email.policy import HTTP
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework import viewsets
from .models import Group, UserGroup, Tag
from .serializers import GroupSerializer, TagSerializer
from .pagination import Pagination


class GroupList(APIView):
    paginator = Pagination
    def get(self, request):
        uid = request.GET.get('uid')
        if uid:
            print(uid)
            groupIds = UserGroup.objects.all().filter(user_id=uid).values_list('group_id', flat=True)
            groups = Group.objects.filter(id__in=groupIds)
            print(groupIds)
            
            # groups = Group.objects.all()
        else:
            groups = Group.objects.all()
        paginator = Pagination()
        result_page = paginator.paginate_queryset(groups, request)
        serializer = GroupSerializer(result_page, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, requst):
        serializer = GroupSerializer(data=requst.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupDetail(APIView):
    
        def get(self, request, pk):
            group = Group.objects.get(pk=pk)
            serializer = GroupSerializer(group)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
        def patch(self, request, pk):
            group = Group.objects.get(pk=pk)
            serializer = GroupSerializer(group, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
        def delete(self, request, pk):
            group = Group.objects.get(pk=pk)
            group.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

class GroupTagList(APIView):
    def get(self, request, gid):
        tags = Tag.objects.all().filter(group_id=gid)
        serializer = TagSerializer(tags, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GroupUserList(APIView):
    def get(self, request, gid):
        users = UserGroup.objects.all().filter(group_id=gid, approved=True).values_list('user_id', flat=True)
        paginator = Pagination()
        result_page = paginator.paginate_queryset(users, request)
        # serializer = UserSerializer(users, many=True)
        return Response(result_page, status=status.HTTP_200_OK)


class GroupUserDetail(APIView):
    def post(self, request, gid, uid):
        if not UserGroup.objects.filter(user_id=uid, group_id=gid).exists():
            user_group = UserGroup(user_id=uid, group_id=gid)
            group = Group.objects.get(pk=gid)
            if group.allow_without_approval:
                user_group.approved = True
            user_group.save()
        return Response(status=status.HTTP_200_OK)
    
    def delete(self, request, gid, uid):
        user_group = UserGroup.objects.get(user_id=uid, group_id=gid)
        user_group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def put(self, request, gid, uid):
        # TODO add admin validation
        user_group = UserGroup.objects.get(user_id=uid, group_id=gid)
        user_group.approved = True
        user_group.save()
        return Response(status=status.HTTP_200_OK)
    