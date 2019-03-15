#!/usr/bin/env python3
from plus_online_client import PlusOnlineClient

try:
    from pathlib import Path
except:
    from pathlib2 import Path

tokenFilename = 'token.txt'
loginFilename = 'login.txt'

token = ()

if __name__ == '__main__':
    print('standalone mode')

    plus = PlusOnlineClient()

    username = None
    password = None
    try:
        # check if token file exists
        token_file = Path(tokenFilename)
        if not token_file.is_file():
            # there is no token file. we need it, but to get it we need to ask for credentials (username + password)
            username, password = plus.read_login_else_write()

        username, token = plus.authorize(username, password)
        # above will take care of saving if the file doesn't exist or something

        # print('---Token istnieje')
    except PermissionError as e:
        print('Cannot authorize!')
        print(e)
        exit(-1)

    else:
        summary_str = plus.refreshDetails(token)

        print('Łącznie w tej chwili masz ' + str(plus.getGBamount()).replace('.', ',') + ' GB')

        from sys import platform

        if 'linux' in platform.lower():
            import notify2

            notify2.init('internet komórkowy')
            notification = notify2.Notification('Pozostało ' + (
                ('dużo ' + '(' + str(
                    plus.getGBamount()) + ' GB)') if plus.getGBamount() > 5 else 'coś tam mało') + ' internetów',
                                                '\n'.join([_['summary'] for _ in plus.data_plans]))
            notification.set_category('network')
            notification.show()
else:
    # imported as module
    pass
