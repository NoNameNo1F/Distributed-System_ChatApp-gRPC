import json
import logging
import os
import re
from concurrent import futures
from datetime import datetime, timezone

import grpc
import jwt
from dotenv import load_dotenv
from google.protobuf import empty_pb2

import protobuf.AuthService.auth_pb2 as auth_pb2
import protobuf.AuthService.auth_pb2_grpc as auth_pb2_grpc
import protobuf.ChatService.chat_pb2 as chat_pb2
import protobuf.ChatService.chat_pb2_grpc as chat_pb2_grpc
from utils.chat_service_helpers import *

config = load_dotenv()

class AuthService(auth_pb2_grpc.AuthServiceServicer):
    def __init__(self,chat_service ):
        self.chat_service = chat_service

    def SignUp(self, request, context):
        print(f'[{request.user_name}]: called SignUp')
        # Register the user and return user_id
        username = str(request.user_name)
        password = str(request.password)
        user_id = self.chat_service.current_user_id
        self.chat_service.user_database[username] = {'user_id': user_id, 'password': password}
        self.chat_service.current_user_id += 1

        self.chat_service.private_chats_db[f'{user_id}'] = {}

        self.chat_service.save_chat_data()

        return auth_pb2.SignUpResponse(user_id=user_id)

    def SignIn(self, request, context):
        # Authenticate user and return user_id and access_token
        print(f'[{request.user_name}]: called SignIn')
        username = str(request.user_name)
        password = str(request.password)
        if username in self.chat_service.user_database and self.chat_service.user_database[username]['password'] == password:
            user_id = int(self.chat_service.user_database[username]['user_id'])

            metadata = get_metadata(self.chat_service.group_id_cnt,
                                    self.chat_service.group_chats_db,
                                    self.chat_service.private_chats_db)
            data = encode_metadata(metadata, key=JWT_SECRET)

            return auth_pb2.SignInResponse(user_id=user_id,user_name=username, metadata=data)
        else:
            return auth_pb2.SignInResponse(user_id=None)

    def SignOut(self, request, context):
        return empty_pb2.Empty()


class ChatService(chat_pb2_grpc.ChatServiceServicer):
    def __init__(self):
        self.user_database = {}
        self.current_user_id = 0
        self.group_id_cnt = 0
        self.group_chats_db = {}
        self.private_chats_db = {}
        self.load_chat_data()

    def get_data_file_path(self):
        # Get the path to the data directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(current_dir, 'data')
        # Return the path to the data.json file
        return os.path.join(data_dir, 'data.json')

    def load_chat_data(self):
        try:
            # Load chat data from a JSON file
            with open(self.get_data_file_path(), 'r') as file:
                data = json.load(file)
                self.user_database = data['user_database']
                self.current_user_id = int(data['current_user_id'])
                self.group_id_cnt = int(data['group_id_cnt'])
                self.group_chats_db = data['group_chats_db']
                self.private_chats_db = data['private_chats_db']
        except FileNotFoundError:
            # If the file doesn't exist, initialize chat data with default values
            self.user_database = {}
            self.current_user_id = 0
            self.group_id_cnt = 0
            self.group_chats_db = {}
            self.private_chats_db = {}

        return self

    def save_chat_data(self):
        # Save chat data to a JSON file
        data = {
            'user_database': self.user_database,
            'current_user_id': self.current_user_id,
            'group_id_cnt': self.group_id_cnt,
            'group_chats_db': self.group_chats_db,
            'private_chats_db': self.private_chats_db
        }

        with open(self.get_data_file_path(), 'w') as file:
            json.dump(data, file)

    def SendMessage(self, request, context):
        print(f'[{request.user_name}]: called SendMessage')
        user_id = request.user_id
        user_name = request.user_name
        message = request.message
        create_at = request.create_at

        new_msg = {
            'user_id': user_id,
            'user_name': user_name,
            'message': message,
            'create_at': create_at,
        }
        # Request Message Chat Group
        if request.group_id != 0:
            group_id = request.group_id
            self.group_chats_db = send_message_to_group(self.group_chats_db, group_id, new_msg)

        # Request Message Private Chat
        elif request.recipient_user_id != 0:
            recipient_user_id = request.recipient_user_id
            # Retrieve username tu auth_service
            recipient_user_name = get_user_name(self.user_database, recipient_user_id)
            # Checking recipient_username
            if recipient_user_name == None:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("UserId not found")
                return empty_pb2.Empty()

            # Update db chat sender send to receiver
            self.private_chats_db = send_message_to_user(self.private_chats_db, user_id, recipient_user_id, recipient_user_name, new_msg)

            # Update back receiver received from sender
            self.private_chats_db = send_message_to_user(self.private_chats_db, recipient_user_id, user_id, user_name, new_msg)

            self.save_chat_data()
            self.load_chat_data()
        else:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("Data not appropriate")
            return empty_pb2.Empty()

        return empty_pb2.Empty()

    def FetchMetadata(self, request, context):
        print(f'[ClientUpdate]: called FetchMetadata')
        metadata = get_metadata(self.group_id_cnt,
                                    self.group_chats_db,
                                    self.private_chats_db)

        data = encode_metadata(metadata, key=JWT_SECRET)
        return chat_pb2.Metadata(metadata=data)

    def CreateGroup(self, request, context):
        print(f'[{request.user_id}]: Create New Group')
        user_id = request.user_id
        group_name = request.group_name
        if user_id is not None:
            self.group_id_cnt += 1
            group_id = self.group_id_cnt
            self.group_chats_db[f'group{group_id}'] = {
                'group_name': group_name,
                'member_ids': [user_id],
                'message_db': {},
                'msg_group_count': 0
            }

            self.save_chat_data()
            self.load_chat_data()

            metadata = get_metadata(self.group_id_cnt,
                                    self.group_chats_db,
                                    self.private_chats_db)

            data = encode_metadata(metadata, key=JWT_SECRET)


            return chat_pb2.Metadata(metadata=data)

    def AddUserToGroup(self, request, context):
        user_id = request.user_id
        group_id = request.group_id
        print(f'[{group_id}]: added user {user_id}')

        if user_id not in self.group_chats_db[f'group{group_id}']['member_ids']:
            self.group_chats_db[f'group{group_id}']['member_ids'].append(user_id)

            self.save_chat_data()
            self.load_chat_data()

            metadata = get_metadata(self.group_id_cnt,
                                    self.group_chats_db,
                                    self.private_chats_db)

            data = encode_metadata(metadata, key=JWT_SECRET)

            return chat_pb2.Metadata(metadata=data)

    def GetListUser(self, request, context):
        print(f'[Client]: called GetListUser')
        user_id = request.user_id

        list_user = {key: value['user_id'] for key, value in self.user_database.items() if value['user_id'] != user_id}

        return chat_pb2.ListUsersResponse(user_list=json.dumps(list_user))

def serve():
    global HOST
    global PORT
    global JWT_SECRET

    HOST = os.environ.get('HOST')
    PORT = os.environ.get('PORT')
    JWT_SECRET = os.environ.get('JWT_SECRET')
    chat_service = ChatService()
    auth_service = AuthService(chat_service)
    #chat_service = ChatService(auth_service)

    address = f"{HOST}:{PORT}"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    auth_pb2_grpc.add_AuthServiceServicer_to_server(auth_service, server)
    chat_pb2_grpc.add_ChatServiceServicer_to_server(chat_service, server)

    server.add_insecure_port(address)
    logging.info("Starting server on %s", address)
    print(f"gRPC Server is started!")
    print("################### Event Capture #################")
    server.start()
    server.wait_for_termination()



if __name__ == '__main__':
    serve()
