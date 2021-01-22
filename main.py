
import requests
import time
import random
import json
import logging
import sys


PASSWORDFILE = 'email_pw.txt'
# first line: email, second: password


# change to your needs
USERAGENT = 'Mozilla/5.0 (X11; Linux x86_64)' + \
            'AppleWebKit/537.36 (KHTML, like Gecko)' + \
            'Chrome/87.0.4280.141 Safari/537.36'

logger = logging.getLogger()


class DeepLQuery:


    def __init__(self, email, password):

        self.email = email
        self.password = password

        self.id = self._create_id()
        self.session = requests.Session()
        self.session.headers['User-Agent'] = USERAGENT

        r = self.session.get("https://www.deepl.com/translator")
        if r.status_code != 200:
            logger.error('error calling deepl.com')
            return
        r = self.session.get("https://static.deepl.com/css/deepl.$0ab019.css",
                                headers={'referer': "https://www.deepl.com/translator"})
        if r.status_code != 200:
            logger.error('error getting css 1')
            return
        #r = self.session.get("https://static.deepl.com/css/cookieBanner.$21aa7c.css",
                                #headers={'referer': "https://www.deepl.com/translator"})
        #if r.status_code != 200:
            #logger.error('error getting css 2')
            #return
        if not self.session.cookies.keys():
            logger.error('didnt get cookie')
            return

        logger.info('waiting 2sec before login')
        time.sleep(2)

        r = self.session.post('https://www.deepl.com/PHP/backend/account.php?request_type=jsonrpc&il=EN',
                                json={"jsonrpc": "2.0",
                                      "method": "login42",
                                      "params": {
                                            "email": self.email,
                                            "password": self.password,
                                            "keepLogin": True
                                      },
                                      "id": self.id
                                },
                                headers={'referer': "https://www.deepl.com/translator"})
        if r.status_code != 200:
            logger.error('login returned error')
            return

        self.id += 1
        # clientState request

        self.id = self._create_id()
        r = self.session.post('https://www.deepl.com/PHP/backend/account.php?request_type=jsonrpc&il=EN',
                                json={"jsonrpc": "2.0",
                                      "method": "getUserDisplayName",
                                      "params": {},
                                      "id": self.id
                                },
                                headers={'referer': "https://www.deepl.com/translator"})
        if r.status_code != 200:
            logger.error('login +1 returned error')
            return

        self.id += 1
        r = self.session.post('https://www.deepl.com/PHP/backend/account.php?request_type=jsonrpc&il=EN',
                                json={"jsonrpc": "2.0",
                                      "method": "getActiveSubscriptionInfo",
                                      "params": {},
                                      "id": self.id
                                },
                                headers={'referer': "https://www.deepl.com/translator"})
        if r.status_code != 200:
            logger.error('login +2 returned error')
            return

        self.id += 1
        # clientState request

        self.id += 1
        r = self.session.post('https://www.deepl.com/PHP/backend/account.php?request_type=jsonrpc&il=EN',
                                json={"jsonrpc": "2.0",
                                      "method": "getActiveSubscriptionInfo",
                                      "params": {},
                                      "id": self.id
                                },
                                headers={'referer': "https://www.deepl.com/translator"})
        if r.status_code != 200:
            logger.error('login +3 returned error')
            return

        logger.info('login seemed to work')
        # fresh id for queries
        #self.id = self._create_id()


    def _create_id(self):
        return 1000 * int(random.random()*1000) + 2

    def query(self, q):
        self.id += 1
        timestamp = int(time.time()*100)

        jj = {
            "jsonrpc": "2.0",
            "method": "LMT_handle_jobs",
            "params": {
                "jobs": [{
                    "kind": "default",
                    "raw_en_sentence": q,
                    "raw_en_context_before": [],
                    "raw_en_context_after": [],
                    "preferred_num_beams": len(q),
                    "quality": "fast"
                }],
                "lang": {
                    "user_preferred_langs": ["DE","EN"],
                    "source_lang_user_selected": "auto",
                    "target_lang": "EN"
                },
                "priority": 1,
                "commonJobParams": {},
                "timestamp": timestamp
            },
            "id": self.id
        }

        r = self.session.post("https://api.deepl.com/jsonrpc",
                                json=jj,
                                headers={'referer': "https://www.deepl.com/"})
        if r.status_code != 200:
            logger.error('error getting main query')
            logger.error(f'r.status_code: {r.status_code}')
            logger.error(f'r.content: {r.content}')
            logger.error(f'id: {self.id}')
            return

        response = json.loads(r.content)

        for beam in response['result']['translations'][0]['beams']:
            return beam['postprocessed_sentence']


    def logout(self):
        self.id += 1
        r = self.session.post('https://www.deepl.com/PHP/backend/account.php?request_type=jsonrpc&il=EN',
                                json={"jsonrpc": "2.0",
                                      "method": "logout",
                                      "params": {},
                                      "id": self.id
                                },
                                headers={'referer': "https://www.deepl.com/translator"})
        if r.status_code != 200:
            logger.error('logout returned error')
            return


if __name__ == '__main__':

    with open(PASSWORDFILE) as pwfile:
        email, password = pwfile.read().strip().split('\n')

    dlq = DeepLQuery(email, password)

    while True:
        print('Type query:')
        inp = sys.stdin.readline().strip()
        if inp == 'q':
            dlq.logout()
            break
        print(dlq.query(inp))

