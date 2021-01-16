
import requests
import time
import sys
import random
import json


session = requests.Session()

session.headers['User-Agent'] = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"

r = session.get("https://www.deepl.com/translator")
if r.status_code != 200:
    print('error calling deepl.com')
    sys.exit()
r = session.get("https://static.deepl.com/css/deepl.$b89835.css", headers={'referer': "https://www.deepl.com/translator"})
if r.status_code != 200:
    print('error getting css 1')
    sys.exit()
r = session.get("https://static.deepl.com/css/cookieBanner.$21aa7c.css", headers={'referer': "https://www.deepl.com/translator"})
if r.status_code != 200:
    print('error getting css 2')
    sys.exit()

if not session.cookies.keys():
    print('didnt get cookie')
    sys.exit()

timestamp = int(time.time()*100)
id = 1000 * int(random.random()*1000) + 2

query = 'fish soup'

jj = {"jsonrpc":"2.0","method": "LMT_handle_jobs","params":{"jobs":[{"kind":"default","raw_en_sentence":query,"raw_en_context_before":[],"raw_en_context_after":[],"preferred_num_beams":len(query),"quality":"fast"}],"lang":{"user_preferred_langs":["DE","EN"],"source_lang_user_selected":"auto","target_lang":"DE"},"priority":-1,"commonJobParams":{},"timestamp":timestamp},"id":id}

r = session.post("https://www2.deepl.com/jsonrpc", json=jj)
if r.status_code != 200:
    print('error getting main query')
    sys.exit()

response = json.loads(r.content)

for beam in response['result']['translations'][0]['beams']:
    print(beam['postprocessed_sentence'])

