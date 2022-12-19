from django.urls import re_path
from rest_framework.urlpatterns import format_suffix_patterns
from . import views

urlpatterns = [
    re_path(r'^groups$', views.GroupList.as_view()),
    re_path(r'^groups/(?P<pk>[0-9]+)$', views.GroupDetail.as_view()),

    re_path(r'^groups/(?P<pk>[0-9]+)/tags$', views.GroupTagList.as_view()),

    re_path(r'^groups/(?P<gid>[0-9]+)/users$', views.GroupUserList.as_view()),
    re_path(r'^groups/(?P<gid>[0-9]+)/users/(?P<uid>[0-9]+)$', views.GroupUserDetail.as_view()),

    re_path(r'^tags/batch$', views.TagBatch.as_view()),

    re_path(r'^likes$', views.LikeDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)