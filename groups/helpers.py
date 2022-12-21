from .models import Like, Tag
from .serializers import TagSerializer, GroupSerializer
import environ
import requests

env = environ.Env()
environ.Env.read_env()

MESSAGE_TYPE_INVITATION = 2
MESSAGE_TYPE_MANAGE = 3

USER_SERVICE = env('USER_SERVICE')
MESSAGE_SERVICE = env('MESSAGE_SERVICE')
POST_MESSAGE_PATH = env('POST_MESSAGE_PATH')
GET_USER_PATH = env('GET_USER_PATH')
POST_USER_BATCH_PATH = env('POST_USER_BATCH_PATH')


def get_tags_json(user_from_id, user_to_id, gid):
    likes = Like.objects.all().filter(user_id_from=user_from_id, user_id_to=user_to_id, group_id=gid)
    likes_tags_ids = likes.values_list('tag_id', flat=True)
    matches_tags_ids = [id for like in likes if like.processed]
    # rev_likes_tags_ids = Like.objects.all().filter(user_id_from=user_to_id, user_id_to=user_from_id, group_id=gid).values_list('tag_id', flat=True)
    # matches_tags_ids = [id for id in likes_tags_ids if id in rev_likes_tags_ids]

    likes_tags = Tag.objects.all().filter(id__in=likes_tags_ids)
    tags_json = TagSerializer(likes_tags, many=True).data
    for tag in tags_json:
        tag['is_match'] = True if tag['id'] in matches_tags_ids else False
    return tags_json



def get_users_by_emails(emails):
    data = {'uids': [], 'emails': emails}
    url = f'{USER_SERVICE}{POST_USER_BATCH_PATH}'

    rsp = requests.post(url, json=data)
    if rsp.status_code != 200:
        print(f'[ERROR] get user ids by emails failed, emails: {emails}')
        return []
    else:
        return rsp.json()['emails']



def send_invitation_message(group, user_from_id, user_to_id):
    user_url_base = f'{USER_SERVICE}{GET_USER_PATH}/'
    user_from = requests.get(f'{user_url_base}{user_from_id}').json()
    user_to = requests.get(f'{user_url_base}{user_to_id}').json()
    
    message_url = f'{MESSAGE_SERVICE}{POST_MESSAGE_PATH}'

    invitation_msg = {
        'content': {
            'from_user': user_from['profile'],
            'to_user': user_to['profile'],
            'group': GroupSerializer(group).data,
            'has_accept': False,
        },
        'type': MESSAGE_TYPE_INVITATION,
        'uid': user_from['id'],
        'email': user_from['email'],
        'has_read': False,
    }
    send_request(message_url, 'POST', invitation_msg)

    if group.allow_without_approval or group.admin_user_id == user_from_id:
        return
    
    admin_user = requests.get(f'{user_url_base}{group.admin_user_id}').json()
    manage_msg = {
        'content': {
            'from_user': user_from['profile'],
            'to_user': user_to['profile'],
            'group': GroupSerializer(group).data,
        },
        'type': MESSAGE_TYPE_MANAGE,
        'uid': admin_user['id'],
        'email': admin_user['email'],
        'has_read': False,
    }
    send_request(message_url, 'POST', manage_msg)

    return


def send_request(url, method, data=None):
    rsp = requests.request(method, url, json=data)
    if rsp.status_code != 200:
        print(f'[ERROR] send {data} to {url} failed: {rsp.text}')
        return None
    else:
        return rsp.json()