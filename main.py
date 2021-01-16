
import requests
import time
import random
import json
from user_agent import generate_user_agent


def queryDeepL(query="bubblegum"):
    session = requests.Session()
    session.headers['User-Agent'] = generate_user_agent()

    r = session.get("https://www.deepl.com/translator")
    if r.status_code != 200:
        print('error calling deepl.com')
        return
    r = session.get("https://static.deepl.com/css/deepl.$b89835.css", headers={'referer': "https://www.deepl.com/translator"})
    if r.status_code != 200:
        print('error getting css 1')
        return
    r = session.get("https://static.deepl.com/css/cookieBanner.$21aa7c.css", headers={'referer': "https://www.deepl.com/translator"})
    if r.status_code != 200:
        print('error getting css 2')
        return

    if not session.cookies.keys():
        print('didnt get cookie')
        return

    timestamp = int(time.time()*100)
    id = 1000 * int(random.random()*1000) + 2

    jj = {"jsonrpc":"2.0","method": "LMT_handle_jobs","params":{"jobs":[{"kind":"default","raw_en_sentence":query,"raw_en_context_before":[],"raw_en_context_after":[],"preferred_num_beams":len(query),"quality":"fast"}],"lang":{"user_preferred_langs":["DE","EN"],"source_lang_user_selected":"auto","target_lang":"DE"},"priority":-1,"commonJobParams":{},"timestamp":timestamp},"id":id}

    r = session.post("https://www2.deepl.com/jsonrpc", json=jj)
    if r.status_code != 200:
        print('error getting main query')
        return

    response = json.loads(r.content)

    for beam in response['result']['translations'][0]['beams']:
        print(beam['postprocessed_sentence'])


if __name__ == '__main__':
    queryDeepL()

