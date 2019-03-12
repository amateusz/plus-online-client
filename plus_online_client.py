#!/usr/bin/env python3

import requests
try:
    from pathlib import Path
except:
    from pathlib2 import Path

tokenFilename = 'token.txt'
loginFilename = 'login.txt'

token = ()

client = {'id': '',
          'msisdn': -1,
          'MBdueTo': '',
          'MBamount': -1
          }

def read_login_else_write():
    login_file = Path(loginFilename)
    if not login_file.is_file():
        # there  even isn't login file. ask for these details
        username = input('Podaj login: ')
        password = input('Podaj haseło (4 ostatnie cyfry PUKa): ')
        with open(login_file, 'w') as file:
            file.write('\n'.join([username, password]))
    else:
        # read from login file and generate from there
        with open(login_file, 'r') as file:
            username, password = file.read().splitlines()
    return username, password

def main():
    username = None
    password = None
    try:
        if __name__ == '__main__':
            # check if token file exists
            token_file = Path(tokenFilename)
            if not token_file.is_file():
                # there is no token file. we need it, but to get it we need to ask for credentials (username + password)
                username, password = read_login_else_write()

            username, token = authorize(username, password)
            # above will take care of saving if the file doesn't exist or something

            # print('---Token istnieje')
    except PermissionError as e:
        print('Cannot authorize!')
        print(e)
        exit(-1)

    # make the actuall request 
    result, detailsJson = getDetails(username, token)
    while not result:
    	# get new token
        username, password = read_login_else_write()

        success = False
        while not success:
            try:
                username, token = authorize(username, password)
                success = True
            except BrokenPipeError:
                from time import sleep
                sleep (.8)
        result, detailsJson = getDetails(username, token)

    from datetime import datetime, timedelta
    activationDate = datetime.fromtimestamp(detailsJson['customerAccount']['expiryDate']/1000)
    activationDate -= timedelta(days=365)

    for balance in detailsJson['balances']:
        if balance['type'] == 'DATA':
            data_plans = []
            for package in balance['packages']:
                if package['Status'] == 'ACTIVE':
                    if package['name'] == '10 GB po doladowaniu/30 dni':
                        valid_for = 30
                    elif package['name'] == 'Pakiet Bonus 30 GB na rok jest włączony.':
                        valid_for = 365
                    elif package['name'] == 'Pakiet 30 GB na start jest włączony.':
                        valid_for = 15

                    data_plans.append({'valid_for': (activationDate - datetime.now() + timedelta(days=valid_for)).days, \
                                       'remain': package['remain'], \
                                       'initially': package['all'] })

            from operator import itemgetter

            data_plan_notification_str = []
            for data_plan in (sorted(data_plans, key=itemgetter('valid_for'))):
            	valid_for_str = str(data_plan['valid_for']).rjust(3) + ' dni:' if data_plan['valid_for'] >1 else ' dzień:'
            	amounts_str = format(data_plan['remain'], '.1f').replace('.', ',') + ' GB z ' + str(int(round(data_plan['initially']))) +' GB'
            	print(valid_for_str + '\t' + amounts_str)
            	data_plan_notification_str.append( format(data_plan['remain'], '.1f').replace('.', ',') + ' GB przez ' + str(data_plan['valid_for']) + ' dni' if data_plan['valid_for'] >1 else ' dzień')



            sum_remain = sum([_['remain'] for _ in data_plans])
            print('Łącznie w tej chwili masz ' + str(sum_remain).replace('.', ',') + ' GB')

            from sys import platform
            if 'linux' in platform.lower():
            	import notify2
            	notify2.init('internet komórkowy')
            	notification = notify2.Notification('Pozostało ' + (('dużo ' + '(' + str(sum_remain) + ' GB)') if sum_remain>5 else 'coś tam mało') + ' internetów', '\n'.join(data_plan_notification_str))
            	notification.set_category('network')
            	notification.show()


def authorize(username=None, password=None):
    """Tries to load long term token from file. If not found takes /username/ and /password/ and generates long term token and saves it in working folder.\nIf no credientials provided and no file is fount, then raises exception."""

    if (username is not None or password is not None) and (username is not '' and password is not ''):
        print('no to zgarniam nowy token')
        tokenResult = getNewToken(username, password)
        if tokenResult[0] == True:
            # obtained correct token
            token = tokenResult[1]
            try:
                tokenFile = open(tokenFilename, 'w')
                # tokenFile.write(token[0] + '\n' + token[1])
                tokenFile.write('\n'.join([username, token]))
                tokenFile.close()
                return (username, token)
            except:
                raise
                # error writing token to file.
        else:
            if tokenResult[1] == 500:
                raise BrokenPipeError
            else:
                raise PermissionError('Wrong credientals!')
            # exit(-1)  # no stored token found and getting new token failed
    else:
        try:
            tokenFile = open(tokenFilename, 'r')
            username, token = tokenFile.read().splitlines()
            tokenFile.close()
            return (username, token)
        except FileNotFoundError:
            raise FileNotFoundError('Creating \"' + tokenFilename + '\"')
        except IOError:
            raise IOError('Provide either user credentials or file with token!')
            # uf there is no file, get them new tokens

def getNewToken(username, password):

    url = {'host': 'https://neti.plus.pl',
           'path': '/neti-rs/login/level23'}
    headers = {'Content-Type': 'application/json',
               'User-Agent': 'Windows tablet'}
    from json import dumps
    payload = dumps({'msisdn': username, 'password': password})

    response = requests.post(url=url['host'] + url['path'], data=payload, headers=headers)
    # print(response.text)
    if response.status_code != 200:
        return (False, response.status_code, 'error', 'Probably expired token - try again or something')
    else:
        from json import loads
        from json.decoder import JSONDecodeError
        try:
            jsonResponse = loads(response.text)
            token = jsonResponse['token']
            return (True, token)
        except JSONDecodeError:
            return (False, response.status_code, 'error', 'Wrong credentials')

def getDetails(msisdn, token):

    url = {'host': 'https://neti.plus.pl',
           'path': '/neti-rs/startup/xhdpi'}
    headers = { 'msisdn': msisdn,
                'authToken': token,
               'User-Agent': 'Windows tablet'}

    response = requests.get(url = url['host'] + url['path'], headers=headers)
    from json import loads
    from json.decoder import JSONDecodeError
    try:
        return (True, loads(response.text))
    except JSONDecodeError:
        return (False, 'token doesn\'t work')

main()
