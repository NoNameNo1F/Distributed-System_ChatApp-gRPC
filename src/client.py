import os
import re
import threading
from datetime import datetime, timezone

import grpc
import PySimpleGUI as sg
from dotenv import load_dotenv
from google.protobuf import empty_pb2

import protobuf.AuthService.auth_pb2 as auth_pb2
import protobuf.AuthService.auth_pb2_grpc as auth_pb2_grpc
import protobuf.ChatService.chat_pb2 as chat_pb2
import protobuf.ChatService.chat_pb2_grpc as chat_pb2_grpc
from pages.authPage import *
from pages.chatPage import *
from utils.chat_service_helpers import *

config = load_dotenv()

def fetch_messages_from_server(chat_stub):
    while True:
        response = chat_stub.FetchMetadata(empty_pb2.Empty())
        yield decode_metadata(response.metadata, JWT_SECRET)
        #time.sleep(5)

def main():
    # global variables
    global HOST
    global PORT
    global JWT_SECRET
    global db_service
    HOST = os.environ.get('HOST')
    PORT = os.environ.get('PORT')
    JWT_SECRET = str(os.environ.get('JWT_SECRET'))

    # Create channel
    address = f"{HOST}:{PORT}"
    channel = grpc.insecure_channel(address)
    # Create gRPC stub
    auth_stub = auth_pb2_grpc.AuthServiceStub(channel)
    chat_stub = chat_pb2_grpc.ChatServiceStub(channel)

    auth_window = create_login_layout()
    # Declare variables

    user_id = 0
    user_name = ""
    chat_window = None
    metadata = ""
    db_service = {}
    group_id = "group0"
    recipient_id = 0
    listuser_response = {}
    threading.Thread(target=fetch_messages_from_server, args=(chat_stub,)).start()

    while True:
        window, event, values = sg.read_all_windows(timeout=100)
        db_service = next(fetch_messages_from_server(chat_stub))

        if event == sg.WIN_CLOSED or event == 'Exit':
            sg.user_settings_set_entry('-location-', window.current_location())
            break

        if window == auth_window:
            if event == 'Sign In':
                username = values['username']
                password = values['password']
                sign_in_request = auth_pb2.SignInRequest(user_name=username, password=password)

                sign_in_response = auth_stub.SignIn(sign_in_request)
                if sign_in_response.user_id:
                    print(f"Sign In Successful! User ID: {sign_in_response.user_id}")
                    user_id = sign_in_response.user_id
                    metadata = sign_in_response.metadata
                    db_service = decode_metadata(metadata, JWT_SECRET)

                    user_name = username

                    listuser_response = chat_stub.GetListUser(chat_pb2.ListUsersRequest(user_id=user_id))

                    auth_window.close()
                    chat_window = create_chat_layout(user_id,user_name,json.loads(listuser_response.user_list), db_service)

                else:
                    print("Sign In Failed!")

            elif event == 'Sign Up':
                username = values['reg_username']
                password = values['reg_password']
                sign_up_request = auth_pb2.SignUpRequest(user_name=username, password=password)

                sign_up_response = auth_stub.SignUp(sign_up_request)
                if sign_up_response.user_id:
                    print("SignUp Successful!")
                else:
                    print("SignUp Failed!")

            elif event == 'Switch to Register':
                auth_window.close()
                auth_window = create_register_layout()

            elif event == 'Switch to Login':
                auth_window.close()
                auth_window = create_login_layout()

        elif window == chat_window and user_id != 0:
            listuser_response = chat_stub.GetListUser(chat_pb2.ListUsersRequest(user_id=user_id))

            if event == sg.WIN_CLOSED or event == 'SignOut':
                # Reset params global variables
                user_id = 0
                user_name = ""
                metadata = ""
                db_service = {}
                group_id = "group0"
                recipient_id = 0
                listuser_response = {}
                chat_window.close()
                auth_window = create_login_layout()

            elif event == 'Send':
                if values['message_input'] == None or values['message_input'] == "":
                    sg.popup("Dont Have Message To ChatWith", title="Warning")
                elif group_id == "group0" or user_id == 0 and values['message_input'] != None:
                    sg.popup("Dont Have Group or Recipient to chat", title="Warning")
                else:
                    message = values['message_input']
                    create_at = datetime.utcnow()
                    msg_send = chat_pb2.Message(user_id=user_id, user_name=username, message=message, create_at=str(create_at), group_id=int(group_id[5:]), recipient_user_id=int(recipient_id))
                    chat_stub.SendMessage(msg_send)
            elif event == 'Create Group':
                create_group_window = create_group_layout()
                while True:
                    event, values = create_group_window.read()

                    if event == sg.WINDOW_CLOSED or event == 'Cancel':
                        # Close the window if the user closes it
                        create_group_window.close()
                        break

                    if event == 'Create':
                        group_name = values['group_name']
                        if group_name != "":
                            # Call gRPC function to create a group
                            create_group_request = chat_pb2.CreateGroupRequest(user_id=user_id, group_name=group_name)
                            create_group_response = chat_stub.CreateGroup(create_group_request)
                            db_service = decode_metadata(create_group_response.metadata, JWT_SECRET)

                        # Close the window after creating the group

                        create_group_window.close()
                        break
                chat_window.close()
                chat_window = create_chat_layout(user_id,user_name,json.loads(listuser_response.user_list), db_service)

            elif event == 'Add User':
                if group_id != "group0":
                    # Server Response User List except User_id
                    user_list = json.loads(listuser_response.user_list)
                    news_list = {}
                    for member in db_service['group_chats_db'][group_id]['member_ids']:
                        for name, id in user_list.items():
                            # thanh vien da ton tai(member)
                            if member != int(id):
                                #user_list.pop(name)
                                news_list.update({name:int(id)})
                    group_name = db_service['group_chats_db'][group_id]['group_name']
                    group_info = {'group_id': group_id,'group_name': group_name}
                    add_user_window = create_add_user_to_group_layout(news_list, group_info)
                    while True:
                        event, values = add_user_window.read()

                        if event == sg.WINDOW_CLOSED or event == 'Cancel':
                            # Close the window if the user closes it
                            add_user_window.close()
                            break

                        if event == 'Add to Group':

                            for key, value in values.items():
                                if value == True:
                                    add_user_to_group_request = chat_pb2.AddUserRequest(user_id=int(key[8:]), group_id=int(group_id[5:]))
                                    response = chat_stub.AddUserToGroup(add_user_to_group_request)
                                    db_service = decode_metadata(response.metadata, JWT_SECRET)

                            # Close the window after creating the group
                            add_user_window.close()
                            chat_window.close()
                            chat_window = create_chat_layout(user_id,user_name,json.loads(listuser_response.user_list), db_service)
                            break

                else:

                    sg.popup("Cannot add other users in private chat.", title="Warning")
                    chat_window.close()
                    chat_window = create_chat_layout(user_id,user_name,json.loads(listuser_response.user_list), db_service)

            elif event.startswith('group'):
                recipient_id = 0
                group_id = event
                print(f'Event: {group_id}')

                history_chat = db_service['group_chats_db'][group_id]
                window['chat_output'].update('')

                if("message_db" in history_chat):
                    history_chat = history_chat['message_db']
                    for msg, msg_data in history_chat.items():
                        if user_id == int(msg_data['user_id']):
                            sg.cprint_set_output_destination(window=window, multiline_key='chat_output')
                            sg.cprint(f'[{msg_data["user_name"]}]:', background_color='orange', font="Franklin 10 bold",text_color='black', end='')
                            sg.cprint(f' {msg_data["message"]}\n',background_color='orange', text_color='black', end='')
                        else:
                            sg.cprint_set_output_destination(window=window, multiline_key='chat_output')
                            sg.cprint(f'[{msg_data["user_name"]}]:', background_color='white', font="Franklin 10 bold", text_color='black', end='')
                            sg.cprint(f' {msg_data["message"]}\n',background_color='white', text_color='black', end='')

            elif event.startswith('user_id'):
                group_id = "group0"
                recipient_id = event[7:]
                print(f'Event: {recipient_id}')

                history_chat = db_service['private_chats_db'][str(user_id)][recipient_id]['message_db']
                window['chat_output'].update('')
                for msg, msg_data in history_chat.items():
                    if int(user_id) == int(msg_data['user_id']):
                        sg.cprint_set_output_destination(window=window, multiline_key='chat_output')
                        sg.cprint(f'[{msg_data["user_name"]}]:', background_color='orange', font="Franklin 10 bold",text_color='black', end='')
                        sg.cprint(f' {msg_data["message"]}\n',background_color='orange', text_color='black', end='')
                    else:
                        sg.cprint_set_output_destination(window=window, multiline_key='chat_output')
                        sg.cprint(f'[{msg_data["user_name"]}]:', background_color='white', font="Franklin 10 bold", text_color='black', end='')
                        sg.cprint(f' {msg_data["message"]}\n',background_color='white', text_color='black', end='')

            elif event == "chatwith":
                group_id = "group0"

                action = values['chatwith']
                pattern = r"\[(.*?)\]"

                print(f'Event: chat with {action}')
                recipient_id = re.search(pattern, action).group(1)

                if recipient_id in db_service['private_chats_db'][str(user_id)]:
                    history_chat = db_service['private_chats_db'][str(user_id)][recipient_id]['message_db']
                    window['chat_output'].update('')
                    for msg, msg_data in history_chat.items():
                        if int(user_id) == int(msg_data['user_id']):
                            sg.cprint_set_output_destination(window=window, multiline_key='chat_output')
                            sg.cprint(f'[{msg_data["user_name"]}]:', background_color='orange', font="Franklin 10 bold",text_color='black', end='')
                            sg.cprint(f' {msg_data["message"]}\n',background_color='orange', text_color='black', end='')
                        else:
                            sg.cprint_set_output_destination(window=window, multiline_key='chat_output')
                            sg.cprint(f'[{msg_data["user_name"]}]:', background_color='white', font="Franklin 10 bold", text_color='black', end='')
                            sg.cprint(f' {msg_data["message"]}\n',background_color='white', text_color='black', end='')
                else:
                    message = f"UserId {user_id}, Want to chat with {action}" if values['message_input'] == "" else values['message_input']
                    create_at = datetime.utcnow()
                    msg_send = chat_pb2.Message(user_id=user_id, user_name=username, message=message, create_at=str(create_at), group_id=int(group_id[5:]), recipient_user_id=int(recipient_id))
                    chat_stub.SendMessage(msg_send)
                chat_window.close()
                chat_window = create_chat_layout(user_id, user_name, json.loads(listuser_response.user_list), db_service)
        else:
            db_service = next(fetch_messages_from_server(chat_stub))
            window = chat_window
            if group_id != "group0":

                db_service = next(fetch_messages_from_server(chat_stub))
                history_chat = db_service['group_chats_db'][group_id]
                window['chat_output'].update('')

                if("message_db" in history_chat):
                    history_chat = history_chat['message_db']
                    for msg, msg_data in history_chat.items():
                        if user_id == int(msg_data['user_id']):
                            sg.cprint_set_output_destination(window=window, multiline_key='chat_output')
                            sg.cprint(f'[{msg_data["user_name"]}]:', background_color='orange', font="Franklin 10 bold",text_color='black', end='')
                            sg.cprint(f' {msg_data["message"]}\n',background_color='orange', text_color='black', end='')
                        else:
                            sg.cprint_set_output_destination(window=window, multiline_key='chat_output')
                            sg.cprint(f'[{msg_data["user_name"]}]:', background_color='white', font="Franklin 10 bold", text_color='black', end='')
                            sg.cprint(f' {msg_data["message"]}\n',background_color='white', text_color='black', end='')
            elif recipient_id != 0:
                db_service = next(fetch_messages_from_server(chat_stub))
                history_chat = db_service['private_chats_db'][str(user_id)][recipient_id]['message_db']
                window['chat_output'].update('')
                for msg, msg_data in history_chat.items():
                    if int(user_id) == int(msg_data['user_id']):
                        sg.cprint_set_output_destination(window=window, multiline_key='chat_output')
                        sg.cprint(f'[{msg_data["user_name"]}]:', background_color='orange', font="Franklin 10 bold",text_color='black', end='')
                        sg.cprint(f' {msg_data["message"]}\n',background_color='orange', text_color='black', end='')
                    else:
                        sg.cprint_set_output_destination(window=window, multiline_key='chat_output')
                        sg.cprint(f'[{msg_data["user_name"]}]:', background_color='white', font="Franklin 10 bold", text_color='black', end='')
                        sg.cprint(f' {msg_data["message"]}\n',background_color='white', text_color='black', end='')

if __name__ == '__main__':
    main()
