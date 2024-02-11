import PySimpleGUI as sg


def create_login_layout():
    layout = [
        [sg.Text('Login', size=(20, 1), font=('Helvetica', 20), justification='center')],
        [sg.Text('Username'), sg.InputText(key='username')],
        [sg.Text('Password'), sg.InputText(key='password', password_char='*')],
        [sg.Button('Sign In'), sg.Button('Switch to Register'), sg.Exit()]
    ]
    return sg.Window('Login', layout, finalize=True)


def create_register_layout():
    layout = [
        [sg.Text('Register', size=(20, 1), font=('Helvetica', 20), justification='center')],
        [sg.Text('Username'), sg.InputText(key='reg_username')],
        [sg.Text('Password'), sg.InputText(key='reg_password', password_char='*')],
        [sg.Button('Sign Up'), sg.Button('Switch to Login'),sg.Exit()]
    ]
    return sg.Window('Register', layout, finalize=True)
