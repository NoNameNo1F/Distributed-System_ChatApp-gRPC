import json
import logging
import time

import grpc
import jwt


def send_message_to_group(group_chats_db, group_id, new_msg):
    groupId = f'group{group_id}'
    groupDB = group_chats_db[groupId]

    # Increase msg_count and create a new msg_id
    groupDB['msg_group_count'] += 1
    msg_id = f'msg{groupDB["msg_group_count"]}'

    # Add new message to message_db
    groupDB['message_db'][msg_id] = new_msg
    return group_chats_db


def get_user_name(user_db, user_id):
    for username, user_info in user_db.items():
        if user_info['user_id'] == user_id:
            return username

    return None

def send_message_to_user(private_chats_db, user_id, recipient_user_id, recipient_user_name, msg):
    chatHistory = private_chats_db.get(str(user_id), {})
    # User chua tung chat truoc kia
    if str(recipient_user_id) not in chatHistory:

        chatHistory[f"{recipient_user_id}"] = {}
        chatHistory[f"{recipient_user_id}"]['recipient_user_name'] = recipient_user_name
        chatHistory[f"{recipient_user_id}"]['message_db'] = {}
        # Set msg_count
        chatHistory[f"{recipient_user_id}"]['msg_count'] = 0

    # 2.1 Sender update msg_db with receiver
    # Increase msg_count and create a new msg_id
    chatHistory[f"{recipient_user_id}"]['msg_count'] += 1
    msg_id = f'msg{chatHistory[str(recipient_user_id)]["msg_count"]}'

    # Add new message to message_db
    chatHistory[f'{recipient_user_id}']['message_db'][msg_id] = msg
    return private_chats_db

def decode_metadata(metadata, key):
    #time.sleep(0.5)
    return jwt.decode(metadata, key, algorithms=['HS256'])

def encode_metadata(metadata, key):
    return jwt.encode(payload=metadata, key=key, algorithm='HS256')

def get_metadata(group_id_cnt, group_chats_db, private_chats_db):
    return {
        'group_id_cnt': group_id_cnt,
        'group_chats_db': group_chats_db,
        'private_chats_db': private_chats_db
    }

