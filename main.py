
import requests
import time
import random
import json
import logging
import sys
from user_agent import generate_user_agent


logger = logging.getLogger()



class DeepLQuery:


    def __init__(self):

        self.id = 1000 * int(random.random()*1000) + 1
        self.session = requests.Session()
        self.session.headers['User-Agent'] = generate_user_agent()

        r = self.session.get("https://www.deepl.com/translator")
        if r.status_code != 200:
            logger.error('error calling deepl.com')
            return
        r = self.session.get("https://static.deepl.com/css/deepl.$b89835.css", headers={'referer': "https://www.deepl.com/translator"})
        if r.status_code != 200:
            logger.error('error getting css 1')
            return
        r = self.session.get("https://static.deepl.com/css/cookieBanner.$21aa7c.css", headers={'referer': "https://www.deepl.com/translator"})
        if r.status_code != 200:
            logger.error('error getting css 2')
            return
        if not self.session.cookies.keys():
            logger.error('didnt get cookie')
            return


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
                    "target_lang": "DE"
                },
                "priority": -1,
                "commonJobParams": {},
                "timestamp": timestamp
            },
            "id": self.id
        }

        r = self.session.post("https://www2.deepl.com/jsonrpc", json=jj)
        if r.status_code != 200:
            logger.error('error getting main query')
            logger.error(f'r.status_code: {r.status_code}')
            logger.error(f'r.content: {r.content}')
            logger.error(f'id: {self.id}')
            return

        response = json.loads(r.content)

        for beam in response['result']['translations'][0]['beams']:
            return beam['postprocessed_sentence']



if __name__ == '__main__':

    dlq = DeepLQuery()

    while True:
        inp = sys.stdin.readline().strip()
        print(dlq.query(inp))

