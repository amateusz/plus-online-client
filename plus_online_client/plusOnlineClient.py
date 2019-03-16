import requests

try:
    from pathlib import Path
except:
    from pathlib2 import Path


class PlusOnlineClient():
    client = {'id': '',
              'msisdn': -1,
              'MBdueTo': '',
              'MBamount': -1
              }

    def __init__(self):
        # self.dataAmount = None  # in GBs
        # self.dueDate = None  # days left to use the data
        self.number = None
        self.id = None  # whatever it is

    def authenticate(self, token):
        pass

    def giveMeToken(self, username=None, password=None):
        '''
        Tries to obtain a new token in exchange for credentials.
        If it doesn't work → Exception
        If there is not one → Exception
        '''

        if (username is not None or password is not None) and (username is not '' and password is not ''):
            print('no to zgarniam nowy token')
            tokenResult = self.__getNewToken(username, password)
            if tokenResult[0] == True:
                # obtained correct token
                token = tokenResult[1]
                return token
            else:
                if tokenResult[1] == 500:
                    raise BrokenPipeError
                else:
                    raise PermissionError('Wrong credientals!')
                # exit(-1)  # no stored token found and getting new token failed

    def read_login_else_write(self, location):
        login_file = Path(location)
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

    def __getNewToken(self, username, password):
        '''
        note: token lifetime is,, very low. ~5 minutes
        :param username:
        :param password:
        :return:
        '''
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

    def getContractData(self, token):
        url = {'host': 'https://neti.plus.pl',
               'path': '/neti-rs/startup/xhdpi'}
        headers = {'msisdn': str(self.number),
                   'authToken': token,
                   'User-Agent': 'Windows tablet'}

        response = requests.get(url=url['host'] + url['path'], headers=headers)
        if response.status_code == 401:
            return (False, 'token properly expired')
        from json import loads
        from json.decoder import JSONDecodeError
        try:
            return (True, loads(response.text))
        except JSONDecodeError:
            return (False, 'token doesn\'t work')

    def refreshDetails(self, token):
        # make the actuall request
        result, detailsJson = self.getContractData(token)
        if not result:
            raise ConnectionError(detailsJson)

        self.data_plans = self.parseDetails(detailsJson)

        from operator import itemgetter
        for data_plan in (sorted(self.data_plans, key=itemgetter('valid_for'))):
            valid_for_str = str(data_plan['valid_for']).rjust(3) + ' dni:' if data_plan['valid_for'] > 1 else ' dzień:'
            amounts_out_of_str = format(data_plan['remain'], '.1f').replace('.', ',') + ' GB z ' + str(
                int(round(data_plan['initially']))) + ' GB'

            summary = valid_for_str + '\t' + amounts_out_of_str

            summary_str = format(data_plan['remain'], '.1f').replace('.', ',') + ' GB przez ' + str(
                data_plan['valid_for']) + ' dni' if data_plan['valid_for'] > 1 else ' dzień'

            # summary_formatted.append(summary_str)

            data_plan.update({'summary': summary_str})
        return summary

    def parseDetails(self, detailsJson):
        from datetime import datetime, timedelta
        activationDate = datetime.fromtimestamp(detailsJson['customerAccount']['expiryDate'] / 1000)
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

                        data_plans.append(
                            {'valid_for': (activationDate - datetime.now() + timedelta(days=valid_for)).days, \
                             'remain': package['remain'], \
                             'initially': package['all']})
                return data_plans

    def setMsisdn(self, msisdn):
        try:
            sanitized = int(msisdn)
            if len(str(msisdn)) != 9:
                raise ValueError  # as well (as above)
        except ValueError:
            print('niepoprawna wartość MSISDN (numeru telefonu). Podaj 9 cyfr.')
        else:
            self.number = sanitized

    def openTokenFromFile(self, location):
        tokenFile = open(location, 'r')
        token = tuple([_ for _ in tokenFile.read().splitlines()])
        tokenFile.close()
        return token

    def saveTokenToFile(self, token, location):
        tokenFile = open(location, 'w')
        # tokenFile.write(token[0] + '\n' + token[1])
        tokenFile.write('\n'.join(list(token)))
        tokenFile.close()

    def getDueToDays(self, total=True):
        if total:
            return sum([_['valid_for'] for _ in self.data_plans])
        else:
            return [_['valid_for'] for _ in self.data_plans]
            # lamda to extract data amoun  # lamda to extract data amount

    def getGBamount(self, total=True):
        if total:
            return sum([_['remain'] for _ in self.data_plans])
        else:
            return [_['remain'] for _ in self.data_plans]
            # lamda to extract data amoun  # lamda to extract data amount
