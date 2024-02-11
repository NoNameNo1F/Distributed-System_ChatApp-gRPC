import threading
import time

import grpc
import PySimpleGUI as sg
from google.protobuf import empty_pb2


def create_chat_layout(user_id, user_name, user_list, chat_serv):
    # Sidebar layout with buttons for groups
    options = []
    for key, value in user_list.items():
        options.append(f'[{value}]{key}')

    navbar = [
        sg.Text('Chatting', text_color="#0C1A39", background_color="#D9BB8A", size=(12, 1),font="Franklin 20 bold"),
        sg.Button('Add User', size=(12, 1), button_color="#EC9B18"),
        sg.Combo(
                values=options,
                font="Franklin 12",
                size=(12, 10),
                default_value=options[0] if options else None,
                enable_events=True,
                readonly=True,
                key='chatwith'
            )
    ]
    sidebar = []
    for group_id in range(1, int(chat_serv['group_id_cnt'])+1):
        if user_id in chat_serv['group_chats_db'][f'group{group_id}']['member_ids']:
            group_name = chat_serv['group_chats_db'][f'group{group_id}']['group_name']
            sidebar.append([sg.Button(group_name,
                           button_color="#0C1A39",
                           size=(12, 1),
                           key=f'group{group_id}')])

    for receipient_id in chat_serv['private_chats_db'][f'{user_id}']:
        chat_with = chat_serv['private_chats_db'][f'{user_id}'][f'{receipient_id}']['recipient_user_name']
        sidebar.append([sg.Button(chat_with,
                                  button_color="#0C1A39",
                                  key=f'user_id{receipient_id}',
                                  size = (12,1)
                                )])

    sidebar.append([sg.Button('Create Group', size=(12, 1), button_color="#EC9B18")])

    # Main layout with sidebar and chat display area
    layout = [
        [
            sg.Text(
                f'Welcome: {user_name}',
                size=(22, 1),
                font="Franklin 12 bold",
                text_color="#0C1A39",
                background_color="#D9BB8A"
            ),
            sg.Push(background_color="#D9BB8A"),
            sg.Button('SignOut', button_color="#0C1A39", size=(12, 1))
        ],
        navbar,
        [
            sg.Column(sidebar, background_color="#D9BB8A", size=(150, 400), scrollable=True),
            sg.Multiline(
                key='chat_output',
                size=(38, 26),
            )
        ],
        [
            sg.Multiline(
                size = (63,2),
                key='message_input',
                do_not_clear=False,
                enter_submits=True,
            )
        ],
        [
            sg.Button('Send', size=(12, 1), button_color='#EC9B18'),
            sg.Push(background_color="#D9BB8A"),
            sg.Button('Exit', button_color="#0C1A39", size=(12, 1))
        ]
    ]
    window = sg.Window('Chat Client', layout, background_color="#D9BB8A", finalize=True, location=sg.user_settings_get_entry('-location-', (None, None)))

    return window

def create_group_layout():
    layout = [
        [sg.Text('Create Group', size=(20, 1), font="Franklin 20 bold")],
        [sg.Text('Group Name'), sg.InputText(key='group_name')],
        [sg.Button('Create'), sg.Button('Cancel')]
    ]
    return sg.Window('Create Group', layout, finalize=True)

def create_add_user_to_group_layout(users, group_info):
    user_choices = [sg.Checkbox(user_name, key=f'add_user{user_id}') for user_name, user_id in users.items()]
    layout = [
        [sg.Text(f'Choose User To Add To {group_info["group_name"]}', key=group_info['group_id'], size=(20, 1), font="Franklin 20 bold", justification='center')],
        user_choices,
        [sg.Button('Add to Group'), sg.Button('Cancel')]
    ]
    return sg.Window(f'Add Users to Group {group_info["group_name"]}', layout, finalize=True)
