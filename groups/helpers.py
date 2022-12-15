import environ
import requests

env = environ.Env()
environ.Env.read_env()

def send_invitation_message(group, user_from_id, user_to_id):
    user_service = env('USER_SERVICE')
    get_user_path = env('GET_USER_PATH')
    user_url_base = f'{user_service}{get_user_path}/'
    user_from = requests.get(f'{user_url_base}{user_from_id}').json()
    user_to = requests.get(f'{user_url_base}{user_to_id}').json()

    message_serivce = env('MESSAGE_SERVICE')
    post_message_path = env('POST_MESSAGE_PATH')
    message_url = f'{message_serivce}{post_message_path}'
    json_data = {
        'count': 1,
        'content': [
            {
                'type': 2, # 2 for invitation
                'userId': user_to['id'],
                'userName': user_to['profile']['name'],
                'userIconId': user_to['profile']['iconId'],
                'groupId': group.id,
                'groupName': group.name,
                'groupIconId': group.icon_id,
                'inviteByUserId': user_from['id'],
                'inviteByUserName': user_from['profile']['name'],
                'inviteByUserIconId': user_from['profile']['iconId'],
                'hasRead': False,
                'hasAccepted': False,
            }
        ]
    }

    rsp = requests.post(message_url, json=json_data)
    if rsp.status_code != 200:
        print(f'[ERROR] send invitation from u:{user_from_id} to u:{user_to_id} on g:{group.id} message failed: {rsp.text}')
    else:
        print(f'[INFO] send invitation from u:{user_from_id} to u:{user_to_id} on g:{group.id} message success')