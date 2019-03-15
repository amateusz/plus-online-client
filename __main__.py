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
    try:
        # check if token file exists
        #token_file = Path(tokenFilename) # seems not used really
        if not token_file.is_file():
            # there is no token file. we need it, but to get it we need to ask for credentials (username + password)
            username, password = plus.read_login_else_write()
            username, token = plus.giveMeToken(username, password)
        else:
            token = plus.openTokenFromFile(tokenFilename)
        plus.saveTokenToFile(tokenFilename)
        # print('---Token istnieje')
    except PermissionError as e:
        print('Cannot authorize!')
        print(e)
        exit(-1)

    else:

        # bash against
        while not result:
            try:
                summary_str = plus.refreshDetails(token)
            except ConnectionError:


            # get new token
            username, password = self.read_login_else_write()
            success = False
            while not success:
                # this shitty API glitches and requires banging
                try:
                    self.number, token = self.giveMeToken(username, password)
                    success = True
                except BrokenPipeError:
                    from time import sleep

                    sleep(.8)
            result, detailsJson = self.getDetails(token)  # i don't like this duplicatin, but…


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
