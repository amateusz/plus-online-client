#!/usr/bin/env python3
from plus_online_client import PlusOnlineClient

try:
    from pathlib import Path
except:
    from pathlib2 import Path
from os import remove

tokenFilename = 'token.txt'
loginFilename = 'login.txt'

token = ()

if __name__ == '__main__':
    '''
    the flow goes like so:
    the API is callable with a token, but this token seems to have very short lifespan.
    Therefor realistically we need to store user credentials or ask for them very often.
    There is no *known* token refresh procedure.
    '''
    print('standalone mode')

    plus = PlusOnlineClient()

    username = None
    password = None
    # get token
    token_valid = False
    while not token_valid:
        # check if token file exists
        token_file = Path(tokenFilename)
        if not token_file.is_file():
            # there is no token file. we need it, but to get it we need to ask for credentials (username + password)
            username, password = plus.read_login_else_write(loginFilename)
            success = False
            while not success:
                # this shitty API glitches and requires banging
                try:
                    token = plus.giveMeToken(username, password)
                    success = True
                except BrokenPipeError:
                    from time import sleep

                    sleep(.8)
                # print('---Token istnieje')
                except PermissionError as e:
                    print('Cannot authorize!')
                    print(e)
                    exit(-1)
            plus.saveTokenToFile((username, token), tokenFilename)
        else:
            try:
                plus.number, token = plus.openTokenFromFile(tokenFilename)
            except FileNotFoundError:
                raise FileNotFoundError('Creating \"' + tokenFilename + '\"')
            except IOError:
                raise IOError('Provide either user credentials or file with token!')
                # uf there is no file, get them new tokens
            # else:
            # here we have loaded a token. does it work
        try:
            # verification
            summary_str = plus.refreshDetails(token)
        except ConnectionError as e:
            from sys import stderr

            print(e, file=stderr)
            # delete current token file, as it's invalid
            remove(token_file)
            # let's keep repeating the loop
        else:
            # got new token and it works
            token_valid = True

        # else:
    # we have a token here already. it might be broken though

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
